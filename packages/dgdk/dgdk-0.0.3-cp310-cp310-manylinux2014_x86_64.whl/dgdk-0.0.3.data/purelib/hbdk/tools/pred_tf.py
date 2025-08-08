r"""
The predictor for tensorflow
"""

import sys
import os
import warnings
import re
from collections import OrderedDict
from functools import cmp_to_key

import numpy as np
import tensorflow as tf
import horizon_plugin_tensorflow
from hbdk.proto import onnx_pb2
from hbdk.operator.conversion import convert_to_hardware_layout
from hbdk.tools.pred import TensorData, get_random_numpy_array, silent_remove_file


def normalize_shape(my_shape, target_shape):
    """Change the num of dim of my_shape to be the same as target_shape, by removing 1's in the shape"""
    len_diff = len(my_shape) - len(target_shape)

    if len_diff == 0:
        return my_shape
    if len_diff < 0:
        return [1] * (-len_diff) + my_shape
    new_shape = []
    for val in my_shape:
        if val == 1 and len_diff > 0:
            len_diff -= 1
        else:
            new_shape.append(val)
    return new_shape


def load_graph_def(model_file):
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    with tf.gfile.GFile(model_file, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    return graph_def


def get_input_shifts(graph_def):
    shifts = []
    for node in graph_def.node:
        if node.op == "BpuQuantiInput":
            shifts.append(node.attr["output_shift"].i)
    return shifts


def get_input_tensor_names(graph_def):
    inputs = []
    for node in graph_def.node:
        if node.op == "Placeholder":
            inputs.append(node.name + ":0")
    return inputs


def get_output_node_names(graph_def):
    input_names, output_names = set(), set()
    for node in graph_def.node:
        output_names.add(node.name)
        input_names.update(set(node.input))
    return list(output_names - input_names)


def get_input_node_names(graph_def):
    inputs = []
    for node in graph_def.node:
        if node.op == "Placeholder":
            inputs.append(node.name)
    return inputs


def reset_shapes(graph_def, ignore_node_names):
    for node in graph_def.node:
        if "_output_shapes" in node.attr:
            del node.attr["_output_shapes"]
        if not node.name in ignore_node_names:
            if node.op == "Placeholder" and "shape" in node.attr:
                orig_shape_num = len(node.attr["shape"].shape.dim)
                del node.attr["shape"]
                node.attr["shape"].CopyFrom(
                    tf.AttrValue(
                        shape=tf.TensorShape([None] *
                                             orig_shape_num).as_proto()))
    return graph_def


def freeze_session(session, output_names):
    graph = session.graph
    with graph.as_default():
        input_graph_def = graph.as_graph_def(add_shapes=True)
        for node in input_graph_def.node:
            node.device = ""
        frozen_graph = tf.graph_util.convert_variables_to_constants(
            session, input_graph_def, output_names)
        return frozen_graph


def infer_shape(graph_def, input_names, input_shapes, output_names):
    node_name_shapes = {}
    for name, shape in zip(input_names, input_shapes):
        if name.count(":") == 0:
            name += ":0"
        node_name_shapes.update({name: shape})

    for node in graph_def.node:
        name = node.name + ":0"
        if name in node_name_shapes.keys():
            shape = node_name_shapes[name]
            orig_shape_num = len(node.attr["shape"].shape.dim)
            assert len(
                shape
            ) >= orig_shape_num, "shape dim for tensor: " + node.name + " in command line is less than shape dim in pb. "
            aligned_shape = shape[len(shape) - orig_shape_num:]
            node_name_shapes[name] = aligned_shape
            node.attr["shape"].CopyFrom(
                tf.AttrValue(shape=tf.TensorShape(aligned_shape).as_proto()))

    with tf.Graph().as_default():
        with tf.Session() as sess:
            tf.import_graph_def(graph_def, name="")
            for name, shape in node_name_shapes.items():
                if name.count(":") == 0:
                    name += ":0"
                tensor = sess.graph.get_tensor_by_name(name)
                tensor.set_shape(shape)
            frozen_graph = freeze_session(sess, output_names)
    return frozen_graph


def filter_im_info_nodes(graph_def, input_node_names):
    ignore_input_node_names = []
    for name in input_node_names:
        for node in graph_def.node:
            if name in node.input and node.op in [
                    "BpuPostProcessRcnn", "BpuQuantiProposal"
            ]:
                node_input_index = list(node.input).index(name)
                if node_input_index == len(
                        node.input) - 1 and 'image_size_fixed' in node.attr:
                    if node.attr['image_size_fixed'].b:
                        input_node_names.remove(name)
                        ignore_input_node_names.append(name)
                break
    return ignore_input_node_names


def handle_input_names(graph_def, input_names, input_shapes, input_node_names):
    model_input_node_names = []
    if input_names:
        # if input name is specified, find out the corresponding placeholder
        assert len(input_names) == len(
            input_shapes
        ), "the number of input shapes and input names must be identical"

        for name in input_names:
            if name in model_input_node_names:
                print("error: found repeated input name", name)
                exit(-1)
            if name in input_node_names:
                model_input_node_names.append(name)
            else:
                print("error: invalid input name", name)
                exit(-1)

    else:
        # otherwise assign the input shapes in order, print out warning
        print(
            "info: \"--input-name\" is not specifed, assigning shapes according to their appearance order"
        )
        model_input_node_names = input_node_names
        assert len(input_node_names) == len(
            input_shapes
        ), "the number of input shapes must agree with the number of input nodes parsed fromd graph def"
        for name, shape in zip(input_node_names, input_shapes):
            for node in graph_def.node:
                if name in node.input:
                    print("info:  assigning shape ", shape, "to placeholder",
                          "\"" + name + "\"", "(input layer",
                          "\"" + node.name + "\")")
                    break
    return model_input_node_names


def handle_input_shapes_names(graph_def, input_shapes, input_names):

    # if --shape is specified, re-assign shapes, this will create a new graph def
    if input_shapes:
        output_node_names = get_output_node_names(graph_def)
        input_node_names = get_input_node_names(graph_def)

        # im info is a placeholder in graph,  but we abandon it when the downstream
        # BpuPostProcessRcnn or BpuQuantiProposal op's "image_size_fixed" attr is true.
        ignore_input_node_names = filter_im_info_nodes(graph_def,
                                                       input_node_names)

        assert len(input_shapes) == len(
            input_node_names
        ), "the number of inputs in command line (%d) " \
           "does not match the number of inputs in pb (%d)" %\
           (len(input_shapes), len(input_node_names))

        # user input names is actually input layer names but not placeholder names,
        # so we MUST to find out the corresponding placeholder names which is essential for shape inferring.
        # if use didn't specify input names, alias shapes with placeholders according to their appearance order
        model_input_node_names = handle_input_names(
            graph_def, input_names, input_shapes, input_node_names)

        # reset "_output_shape" attr in all nodes and "shape" attr in placeholder
        graph_def = reset_shapes(graph_def, ignore_input_node_names)

        return infer_shape(graph_def, model_input_node_names, input_shapes,
                           output_node_names)
    return graph_def


def freeze_graph_def_to_file(graph_def, file_name):
    with tf.gfile.GFile(file_name, "wb") as f:
        f.write(graph_def.SerializeToString())


class TfPredictor:
    """Run predictor(inference) for TF models"""

    def __init__(self, model_file, march, input_shapes, input_names):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        self.model_file = model_file
        self.march = march

        self.graph_def = handle_input_shapes_names(
            load_graph_def(model_file), input_shapes, input_names)
        self._set_dpp_hw_block_size([64, 64, 64, 64, 64], [64, 64, 64, 64, 64])

        tf.compat.v1.reset_default_graph()
        self.ses = tf.compat.v1.Session()

        self.ses.graph.as_default()
        self.graph = self.ses.graph
        tf.import_graph_def(self.graph_def, name="")

        self.tensor_name_to_index = OrderedDict()
        tindex = 0
        for node in self.ses.graph.get_operations():
            for i, t in enumerate(node.inputs):
                self.tensor_name_to_index[t.name] = tindex
                tindex += 1
            for t in node.outputs:
                self.tensor_name_to_index[t.name] = tindex
                tindex += 1

        self.input_tensors = OrderedDict()
        for node in self.ses.graph.get_operations():
            if node.type == "Placeholder":
                for t in node.outputs:
                    self.input_tensors[t.name] = t
            elif node.type == 'BpuQuantiInput':
                for t in node.inputs:
                    if t.name in self.input_tensors:
                        self.input_tensors.pop(t.name)
                for t in node.outputs:
                    self.input_tensors[t.name] = t

        self.tensors_ignored = OrderedDict()  # To hack im_info
        for node in self.ses.graph.get_operations():
            for i, t in enumerate(node.inputs):
                if self.should_ignore_node(node,
                                           i) and t.name in self.input_tensors:
                    self.tensors_ignored[t.name] = t
                elif t.name in self.tensors_ignored:
                    self.tensors_ignored.pop(t.name)

        for tname in self.tensors_ignored.keys():
            if tname in self.input_tensors:
                del self.input_tensors[tname]
                warnings.warn("Input tensor %s is ignored because"
                              " it does not affect the graph" % tname)
        self.input_tensors = self._sort_tensor_container(self.input_tensors)
        self.tensors_ignored = self._sort_tensor_container(
            self.tensors_ignored)

        self.input_tensor_names = list(self.input_tensors.keys())
        self.input_node_names = get_input_tensor_names(self.graph_def)

        self.output_node_names = get_output_node_names(self.graph_def)
        self.output_tensors = OrderedDict()
        for name in self.output_node_names:
            node = self.ses.graph.get_operation_by_name(name)
            for t in node.outputs:
                self.output_tensors[t.name] = t
        self.output_tensor_names = list(self.output_tensors.keys())
        self.input_shifts = get_input_shifts(self.graph_def)

        self.tensor_name_to_hbir_name = {}
        for node in self.ses.graph.get_operations():
            for i, t in enumerate(node.outputs):
                name = node.name
                if i > 0:
                    name = node.name + "_" + str(i)
                self.tensor_name_to_hbir_name[t.name] = name

    def _sort_tensor_container(self, container):
        """Sort OrderedDict/tuple/list of tensor names"""
        if isinstance(container, OrderedDict):
            new = OrderedDict()
            keys = list(container.keys())
            keys = sorted(keys, key=cmp_to_key(self._tensor_cmp))
            for k in keys:
                new[k] = container[k]
        else:
            new = list(container)
            new = sorted(new, key=cmp_to_key(self._tensor_cmp))
            if not isinstance(new, type(container)):
                new = type(container)(new)
        return new

    def _tensor_cmp(self, tensor_name1, tensor_name2):
        """Compare function. Order by index of self.graph.graph_def.node"""
        t1 = self.tensor_name_to_index.get(tensor_name1, 2147483647)
        t2 = self.tensor_name_to_index.get(tensor_name2, 2147483647)
        if t1 != t2:
            return t1 - t2
        if tensor_name1 < tensor_name2:
            return -1
        if tensor_name1 > tensor_name2:
            return 1
        return 0

    def _set_dpp_hw_block_size(self, h_block_size_list, w_block_size_list):
        """Set hw block size list to make pred result consist with bpu"""
        changed = False
        for node in self.graph_def.node:
            if node.op == "BpuQuantiProposal":
                node.attr['h_block_size_list'].CopyFrom(
                    tf.AttrValue(
                        list=tf.AttrValue.ListValue(i=h_block_size_list)))
                node.attr['w_block_size_list'].CopyFrom(
                    tf.AttrValue(
                        list=tf.AttrValue.ListValue(i=w_block_size_list)))
                changed = True
        if changed:
            print("NOTE: BpuQuantiProposal" " block size is set to 64")

    def run_model(self, feed_dict, output_tensor_names):
        """Return predictor and return list of results"""
        feed_dict_with_ignored_inputs = dict(feed_dict)
        # Fill ignored inputs with zero. For example, im_info with image_size_fixed == True
        for name, t in self.tensors_ignored.items():
            shape = t.get_shape().as_list()
            dtype = t.dtype.as_numpy_dtype
            val = np.zeros(shape, dtype)
            feed_dict_with_ignored_inputs[name] = val
        output_values = self.ses.run(
            output_tensor_names, feed_dict=feed_dict_with_ignored_inputs)
        return OrderedDict(zip(output_tensor_names, output_values))

    def get_all_tensor_names(self):
        """The the name of all tensors in model"""
        names = []
        name_dict = {}
        for node in self.ses.graph.get_operations():
            for t in node.inputs:
                if t.name not in name_dict:
                    names.append(t.name)
                    name_dict[t.name] = True
            for t in node.outputs:
                if t.name not in name_dict:
                    names.append(t.name)
                    name_dict[t.name] = True
        return names

    def get_output_tensor_names(self):
        return self.output_tensor_names

    def get_all_tensor_names_without_quantiinput(self):
        """Get the name of all tensors except QuantiInput"""
        names = self.get_all_tensor_names()
        for node in self.ses.graph.get_operations():
            if node.type == "BpuQuantiInput":
                for t in node.inputs:
                    try:
                        names.remove(t.name)
                    except ValueError:
                        pass
        return names

    def _get_tensor_hbir_name(self, node, node_output_index):
        if node_output_index == 0:
            return node.name
        return node.name + "_" + str(node_output_index)

    def add_inhardwarelayout_tensor_values(self, tensor_value_map):
        """Add the values of inhardwarelayout tensors"""
        for node in self.ses.graph.get_operations():
            if all([t.name in tensor_value_map for t in node.outputs]):
                outputs = [tensor_value_map[t.name] for t in node.outputs]
                attr_dict = {}
                for attr_name, _ in node.node_def.attr.items():
                    attr_dict[attr_name] = node.get_attr(attr_name)
                converteds = convert_to_hardware_layout(
                    node, outputs, self.march, node.node_def.op, attr_dict)
                if not converteds:
                    continue
                for i, data in enumerate(converteds):
                    tensor_name = node.name
                    if i > 0:
                        tensor_name += tensor_name + "_" + str(i)
                    tensor_name += "_inhardwarelayout"
                    hbir_name = node.name
                    if i > 0:
                        hbir_name = node.name + "_" + str(i)
                    hbir_name += "_inhardwarelayout"
                    self.tensor_name_to_hbir_name[tensor_name] = hbir_name
                    tensor_value_map[tensor_name] = data
        return tensor_value_map

    def _get_tensor_type(self, tensor_name):
        """(Internal) Get tensor type (model input/output/param/intermediate)"""
        for node in self.ses.graph.get_operations():
            for t in node.outputs:
                if t.name != tensor_name:
                    continue
                if t.name in self.input_tensor_names:
                    return TensorData.MODEL_INPUT
                if t.name in self.output_tensor_names:
                    return TensorData.MODEL_OUTPUT
                return TensorData.MODEL_INTERMEDIATE
        return TensorData.MODEL_PARAM

    def to_onnx(self, tensor_value_map):
        """Conver to Onnx Protobuf"""
        onnx_model = onnx_pb2.ModelProto()
        for name, data in tensor_value_map.items():
            tensor_type = self._get_tensor_type(name)
            name = self.tensor_name_to_hbir_name[name]
            tensor_data = TensorData(name, data, tensor_type)
            tensor_data.add_to_model_proto(onnx_model)
        onnx_model.producer_name = "tensorflow-horizon"
        onnx_model.producer_version = horizon_plugin_tensorflow.__version__
        return onnx_model

    def generate_random_input(self, tensor_name):
        """Generate random inputs"""
        t = self.input_tensors[tensor_name]
        shape = t.get_shape().as_list()
        dtype = t.dtype.as_numpy_dtype
        return get_random_numpy_array(dtype, shape)

    def should_ignore_node(self, node, node_input_index):
        if (node.type == "BpuPostProcessRcnn"
                or node.type == "BpuQuantiProposal") \
                and node_input_index == len(node.inputs) - 1:
            attr_dict = {}
            for attr_name, _ in node.node_def.attr.items():
                attr_dict[attr_name] = node.get_attr(attr_name)
            if str(attr_dict.get('image_size_fixed')) == "True":
                return True
        return False


def main(options):
    """main of predictor for tensorflow"""
    if options['gen_random_param_and_exit']:
        sys.exit(0)
    model_file = options['model']
    assert model_file.endswith(
        '.pb'), "Tensorflow model filename should ends with .pb"
    predictor = TfPredictor(model_file, options['march'], options['shape'], [])
    assert len(options['shape']) == len(predictor.input_tensors), \
        "The number of shape in -s (%d)" \
        " does not match number of inputs in protobuf (%d)" % (
            len(options['shape']), len(predictor.input_tensors))

    input_index = 0
    if options['gen_random_input_and_exit']:
        for name, t in predictor.input_tensors.items():
            a = predictor.generate_random_input(name)
            filename = options['input_binary'][input_index]
            if filename:
                a.tofile(filename)
        sys.exit(0)
    feed_dict = {}
    input_index = 0
    for name, t in predictor.input_tensors.items():
        input_dtype = np.dtype(t.dtype.as_numpy_dtype)
        input_file_name = options['input_binary'][input_index]
        if input_dtype == np.float32:
            input_dtype = np.int32
        a = np.fromfile(input_file_name, dtype=input_dtype)
        if input_file_name.find("_uint8_") != -1:
            a = a + np.iinfo(np.dtype('int8')).min
        a = a.reshape(t.get_shape().as_list())
        feed_dict[name] = a
        input_index += 1

    tensor_value_map = predictor.run_model(
        feed_dict, predictor.get_all_tensor_names_without_quantiinput())
    tensor_value_map = predictor.add_inhardwarelayout_tensor_values(
        tensor_value_map)

    # Output files are named by following rule:
    #
    # hbdk_output_${FEATURE_NAME}.txt
    #
    # Model verifier relies on the file names and headers to compare output tensors.
    # Please modify model verifier's code correspondingly if there is any modification!
    if options['gen_txt_output']:
        os.makedirs(os.path.abspath(options["output"]), exist_ok=True)
        output_tensor_names = predictor.get_output_tensor_names()
        for orig_output_tensor_name in output_tensor_names:
            output_tensor_name = re.split(r'\d+$', orig_output_tensor_name)[0]
            tmp_name1 = output_tensor_name + '_inhardwarelayout'
            tmp_name2 = orig_output_tensor_name + '_inhardwarelayout'
            tmp_name3 = output_tensor_name[0:output_tensor_name
                                           .rfind(':')] + '_inhardwarelayout'
            tmp_name4 = orig_output_tensor_name[
                0:orig_output_tensor_name.rfind(':')] + '_inhardwarelayout'
            tmp_names = [tmp_name1, tmp_name2, tmp_name3, tmp_name4]
            hardwarelayout_output_tesnor_names = []
            for name in tensor_value_map:
                for tmp_name in tmp_names:
                    if name.find(tmp_name) != -1:
                        hardwarelayout_output_tesnor_names.append(name)
            if hardwarelayout_output_tesnor_names:
                for name in hardwarelayout_output_tesnor_names:
                    formated_tensor_name = name.replace('/', '_')
                    output_filename = os.path.join(
                        os.path.abspath(options["output"]),
                        'hbdk_output_' + formated_tensor_name + '.txt')
                    tmp_dim = int(1)
                    data = tensor_value_map[name].data
                    for dim in data.shape:
                        tmp_dim *= dim
                    tmp_dim /= data.shape[-1]
                    tmp_dim = int(tmp_dim)
                    output_reshape = data.obj.reshape((tmp_dim,
                                                       data.shape[-1]))
                    np.savetxt(output_filename, output_reshape, fmt='%.20e')
            else:
                formated_tensor_name = orig_output_tensor_name.replace(
                    '/', '_')
                end_index = formated_tensor_name.index(':')
                formated_tensor_name = formated_tensor_name[:end_index]
                output_filename = os.path.join(
                    os.path.abspath(options["output"]),
                    'hbdk_output_' + formated_tensor_name + '.txt')
                tmp_dim = int(1)
                data = tensor_value_map[orig_output_tensor_name].data
                for dim in data.shape:
                    tmp_dim *= dim
                tmp_dim /= data.shape[-1]
                tmp_dim = int(tmp_dim)
                output_reshape = data.obj.reshape((tmp_dim, data.shape[-1]))
                np.savetxt(output_filename, output_reshape, fmt='%.20e')
    elif options['output']:
        onnx_model = predictor.to_onnx(tensor_value_map)
        silent_remove_file(options["output"])
        with open(options["output"], "wb") as f:
            serialized = onnx_model.SerializeToString()
            if not serialized:
                print('warning: cannot generate output')
            f.write(serialized)
