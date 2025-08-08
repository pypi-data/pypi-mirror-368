# -*- coding: utf-8 -*-
"""Run MXNET predictor"""

import argparse
import functools
import math
import os
import time

import sys

import numpy as np

import hbdk.config

from hbdk.util.exec import register_exit_gracefully_handler


def import_modules():
    """Import is slow and not needed when the result is cached. Delay import until needed"""

    def add_to_globals(**kwargs):
        for k, v in kwargs.items():
            globals()[k] = v

    import array
    add_to_globals(array=array)
    import struct
    add_to_globals(struct=struct)
    import pprint
    add_to_globals(pprint=pprint)
    import random
    add_to_globals(random=random)
    add_to_globals(functools=functools)
    import operator
    add_to_globals(operator=operator)
    # import math
    # add_to_globals(math=math)
    import warnings
    add_to_globals(warnings=warnings)
    import ast
    add_to_globals(ast=ast)
    import json
    add_to_globals(json=json)
    import re
    add_to_globals(re=re)
    from collections import OrderedDict
    add_to_globals(OrderedDict=OrderedDict)

    # import numpy as np
    # add_to_globals(np=np)

    try:
        import mxnet
        add_to_globals(mxnet=mxnet)
        import mxnet_predict
        add_to_globals(mxnet_predict=mxnet_predict)
    except ImportError:
        mxnet = None
        add_to_globals(mxnet=mxnet)
    from hbdk.operator import lut
    add_to_globals(lut=lut)
    from hbdk.proto import onnx_pb2
    add_to_globals(onnx_pb2=onnx_pb2)
    from hbdk.operator.conversion import convert_to_hardware_layout
    add_to_globals(convert_to_hardware_layout=convert_to_hardware_layout)
    from hbdk.util.file import force_symlink
    add_to_globals(force_symlink=force_symlink)

    random.seed(0)  # Use fixed seed to get reproducable param.
    np.random.seed(0)

    if mxnet:
        # MXNET Python3 workarounds:
        # 1. Workaround relative imports
        # 2. Workaround "xrange" not defined
        # 3. Workaround warnings
        # TODO: Remove this when Python3 support is fixed
        sys.path.append(
            os.path.join(os.path.dirname(mxnet.__file__), "plugin", "x2"))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import mxnet.plugin.x2  # pylint: disable=ungrouped-imports

            mxnet.plugin.x2.__builtins__["xrange"] = range
            # pylint: disable=wrong-import-position,ungrouped-imports
            from mxnet.plugin.x2.init import AnchorTableInitializer
            add_to_globals(AnchorTableInitializer=AnchorTableInitializer)
            from mxnet.plugin.x2.init import ExpTableInitializer
            add_to_globals(ExpTableInitializer=ExpTableInitializer)


# NOTE: Update this whenever pred.py (Not MXNET) has any incompatible changes
HBDK_PRED_VERSION = 3.2


def silent_remove_file(filename):
    """
    Call before open(filename, "wb") to solve problem if symlink "filename" already exists
    """
    try:
        os.remove(filename)
    except OSError:
        pass


class TensorData:
    """
    Class to store the name, dim, element type and data of a tensor
    """
    MODEL_INPUT = "model_input"
    MODEL_PARAM = "model_param"
    MODEL_OUTPUT = "model_output"
    MODEL_INTERMEDIATE = "model_intermediate"

    model_proto_input_id = 0

    # Increase by 1 whenever an input tensor is added
    # into the model proto

    def __init__(self, name, data, io_type):
        assert io_type in (self.MODEL_INPUT, self.MODEL_PARAM,
                           self.MODEL_OUTPUT, self.MODEL_INTERMEDIATE)
        self.name = name
        if hasattr(data, "asnumpy"):
            self.data = data.asnumpy()
        else:
            self.data = data  # The data of tensor in Python NDArray
        self.io_type = io_type

    @staticmethod
    def numpy_type_to_onnx_type(numpy_type):
        """Convert onnx type to numpy dtype"""
        elem_type_mapping = {
            np.int8: 'INT8',
            np.int16: 'INT16',
            np.int32: 'INT32',
            np.int64: 'INT64',
            np.uint8: 'UINT8',
            np.uint16: 'UINT16',
            np.uint32: 'UINT32',
            np.uint64: 'UINT64',
            np.bool_: 'BOOL',
            np.float32: 'FLOAT',
            np.float64: 'DOUBLE',
            np.float16: 'FLOAT16',
            np.complex64: 'COMPLEX64',
            np.complex128: 'COMPLEX128',
            np.string_: 'STRING',
        }
        data_type_str = ""
        for dtype, onnx_type in elem_type_mapping.items():
            if numpy_type == dtype:
                data_type_str = onnx_type
                break
        assert data_type_str
        from hbdk.proto import onnx_pb2
        return onnx_pb2.TensorProto.DataType.Value(data_type_str)

    def add_to_model_proto(self, model_proto):
        """
        Convert the ordered dictionary whose key is tensor name and whose
        value is TensorData to onnx ModelProto object
        :return: The onnx ModelProto Object
        """
        tensor = model_proto.graph.initializer.add()
        tensor.dims.extend(list(self.data.shape))
        tensor.name = self.name
        elem_type = self.numpy_type_to_onnx_type(np.dtype(self.data.dtype))
        tensor.data_type = elem_type

        # Although there are several data storage in TensorProto
        # such as int32_data, int64_data
        # We only use raw_data,
        # because those types are only effective when the
        # number is positive and small and in
        # larger element unit such as int32, int64,
        # But we usually only use int8 type, so
        # raw_data is the most efficient.
        # Check out protobuf encoding in google doc to understand why
        tensor.raw_data = self.data.tobytes()

        if self.io_type == self.MODEL_INPUT:
            tensor_proto = model_proto.graph.input.add()
            self.add_to_tensor_proto(tensor_proto)
            input_tag = model_proto.metadata_props.add()
            input_tag.key = "input" + str(self.model_proto_input_id)
            input_tag.value = self.name
            self.model_proto_input_id += 1
        elif self.io_type == self.MODEL_PARAM:
            tensor_proto = model_proto.graph.input.add()
            self.add_to_tensor_proto(tensor_proto)
        elif self.io_type == self.MODEL_INTERMEDIATE:
            tensor_proto = model_proto.graph.value_info.add()
            self.add_to_tensor_proto(tensor_proto)
        elif self.io_type == self.MODEL_OUTPUT:
            tensor_proto = model_proto.graph.output.add()
            self.add_to_tensor_proto(tensor_proto)
        else:
            assert False
        return model_proto

    def add_to_tensor_proto(self, tensor_proto):
        tensor_proto.name = self.name
        tensor_proto.type.tensor_type.elem_type = \
            self.numpy_type_to_onnx_type(np.dtype(self.data.dtype))
        for d in self.data.shape:
            dim = tensor_proto.type.tensor_type.shape.dim.add()
            dim.dim_value = d


def parse_args():
    """
    parse arguments
    :return: a dict containing arguments
    """
    # mandatory
    parser = argparse.ArgumentParser(description="HBDK predictor")
    parser.add_argument(
        '--time',
        nargs="?",
        default=None,
        const="",
        help='Time individual commands',
    )
    parser.add_argument(
        '-m',
        '--model',
        required=True,
        help='MXNet/Tensorflow model (*.json/*.pb)')
    parser.add_argument(
        '--march',
        required=False,  # not for generating params/inputs
        help='The target march architecture.'
        ' Some special operator needs target specific handling.')
    parser.add_argument(
        '-f',
        '--framework',
        required=False,
        help='The deep learning framework to run',
        choices=('mxnet', 'tensorflow', 'hbir', 'torch'),
        default='mxnet')
    parser.add_argument(
        '-p',
        '--param',
        required=False,
        help='MXNet parameters (*.param), generate a random one if not exist')
    parser.add_argument(
        '-s',
        '--shape',
        required=True,
        help='NHWC shape for input features, separated by comma')
    # optional
    parser.add_argument(
        '-b',
        '--input-binary',
        required=False,
        default='',
        help='Binary file (int8) names for input features, separated by comma')
    parser.add_argument(
        '-n',
        '--input-name',
        required=False,
        default='',
        help='Tensor name of input features, separated by comma')
    parser.add_argument(
        '-o',
        '--output',
        required=False,
        default=os.path.join(os.getcwd(), "pred.onnx"),
        help='The path to output predictor result as a single onnx model file')
    parser.add_argument(
        '-d',
        '--debug',
        required=False,
        type=int,
        default=0,
        nargs='?',
        help='Print debugging information, level 0~2')
    parser.add_argument(
        '--gen-random-param-and-exit',
        required=False,
        default=False,
        action='store_true',
        help='Generate random param and then exit')
    parser.add_argument(
        '--zero-param',
        required=False,
        default=False,
        action='store_true',
        help='Generated param are all zero. For internal test ')
    parser.add_argument(
        '--partial-param',
        required=False,
        default=False,
        help='The partial param file.'
        ' If provided, will be used by the random param generator')
    parser.add_argument(
        '--weight-sparsity',
        required=False,
        default='1/1',
        help='Specify weight sparsity ratio (fraction, such as 1/2 or 3/4)'
        ' for generating random param')
    parser.add_argument(
        '--gen-random-input-and-exit',
        required=False,
        default=False,
        action='store_true',
        help='Generate random input and then exit.'
        'Output filename comes from -b option. Empty filename is ignored')
    parser.add_argument(
        '--gen-txt-output',
        required=False,
        default=False,
        action='store_true',
        help='Store output in txt format instead of onnx.')
    parser.add_argument(
        '--large-bias',
        required=False,
        default=False,
        action='store_true',
        help=
        'Generate large bias values that could be decomposed into 2 int8 values'
    )
    parser.add_argument(
        '--complement-weight',
        action='store_true',
        help='for dev use, generate complement weight for adjacent rows/columns'
    )

    parser.add_argument(
        '--cache-root',
        required=False,
        help=
        "The root directory of Predictor result cache folder (For dev use only)"
    )
    parser.add_argument(
        '--cache-server',
        required=False,
        help="The HOST:PORT of server to cache the metadata (For dev use only)"
    )
    parser.add_argument(
        '--update-cache',
        required=False,
        action='store_true',
        help='update cache. Require to specify cache root (For dev use only)')
    parser.add_argument(
        '--example-input',
        required=False,
        help='Specify example input for torch model')
    parser.add_argument(
        '-t',
        '--input-dtypes',
        required=False,
        help='Specify input dtypes for torch input binaries')
    options = vars(parser.parse_args())

    if 'march' not in options or not options['march']:
        if options['gen_random_input_and_exit'] or options[
                'gen_random_param_and_exit']:
            options['march'] = 'x2'  # any march is OK
        else:
            raise RuntimeError(
                'march must be specified when running predictor')

    options['march'] = hbdk.config.get_normalized_march(options['march']).name
    if options['march'] == hbdk.config.March.B253:
        options['march'] = hbdk.config.March.B25
    # assert hbdk.config.is_march_supported(options['march'])

    if options['framework'] == 'mxnet' and not options['param'] \
            and not options['gen_random_input_and_exit']:
        raise RuntimeError('param must be specified when not'
                           ' generating random input when using mxnet')
    # split shape, file name and format for multiple inputs
    shape_strings = tuple(
        shape.strip().lower() for shape in options['shape'].strip().split(','))
    options['shape'] = tuple(
        tuple(int(x)
              for x in shape_string.split('x'))
        for shape_string in shape_strings)
    # assert all([len(x) == 4 for x in options['shape']])

    if options['input_binary'].strip():
        options['input_binary'] = tuple(
            x.strip() for x in options['input_binary'].strip().split(','))
        assert not options['input_binary'] or len(options['shape']) == len(
            options['input_binary']), '%d input shapes, but %d binaries' % \
                                      (len(options['shape']),
                                       len(options['input_binary']))
    else:
        options['input_binary'] = [''] * len(options['shape'])

    if options['input_name'].strip():
        options['input_name'] = tuple(
            x.strip() for x in options['input_name'].strip().split(','))
        assert not options['input_name'] or len(options['shape']) == \
               len(options['input_name']), \
            '%d input shapes, but %d input tensor names' % \
            (len(options['shape']), len(options['input_name']))
        assert options['input_name'][0]
    else:
        options['input_name'] = [''] * len(options['shape'])

    if options['example_input']:
        sys.path.append(os.path.dirname(options['example_input']))
    if options['input_dtypes']:
        options['input_dtypes'] = tuple(
            dtype.strip().lower()
            for dtype in options['input_dtypes'].strip().split(','))
    return options


def dump_to_binary_file(feature_data_type, npa, file_name):
    """
    :param npa: numpy array
    :param file_name: full file name with path
    :return: None
    """
    np_type_to_struct_format_char = {
        np.int8: 'b',
        np.int16: '<h',
        np.int32: '<i',
        np.int64: '<q',
        np.uint8: 'B',
        np.uint16: '<H',
        np.uint32: '<I',
        np.uint64: '<Q',
        np.float32: '<f',
        np.float64: '<d',
        np.double: '<d',
    }
    struct_format_chars = [
        x[1]
        for x in np_type_to_struct_format_char.items()
        if x[0] == feature_data_type
    ]
    assert len(struct_format_chars) == 1
    format_char = struct_format_chars[0]

    silent_remove_file(file_name)
    with open(file_name, 'wb') as f:
        if format_char == 'b':
            values = tuple(npa.reshape(-1))
            # check if the values are properly distributed
            counters = [0] * 256
            sample_number = 100
            if len(values) >= sample_number:
                for v in values[:sample_number]:
                    counters[v] += 1
                checkers = (([-128], 0.6), ([127], 0.6), ([0], 0.6),
                            ([-128, 127], 0.99), ([0, 127], 0.99))
                for vv, percentage in checkers:
                    number = sum([counters[v] for v in vv])
                    if number > sample_number * percentage:
                        print('warning: %s has too many %s (%d out of %d)' %
                              (file_name, str(vv), number, sample_number))
                    else:
                        print(
                            'info: %s has appropriate %s (%d out of %d)' %
                            (file_name, str(vv), number, sample_number),
                            file=sys.stderr)

            array.array(format_char[0], values).tofile(f)
        else:
            for d in npa.reshape(-1):
                f.write(struct.pack(format_char, d))


def dump_to_text_file(npa, file_name):
    """
    :param npa: numpy array
    :param file_name: full file name with path
    :return: None
    """

    silent_remove_file(file_name)
    with open(file_name, 'w') as f:
        if npa.dtype in (np.float32, np.float64, np.double):
            for l in npa.reshape(-1, npa.shape[-1]):
                for d in l:
                    f.write('%.6f\t' % d)
                f.write('\n')
        else:
            for l in npa.reshape(-1, npa.shape[-1]):
                for d in l:
                    f.write('%d\t' % d)
                f.write('\n')


def roi_binary_to_nparray(roi_bytes):
    """
    :param roi_bytes:
    :return:
    """

    # box number:2B padding 2B*7   (total 16 bytes for header)
    # left:2B top:2B right:2B bottom:2B score:1B label:1B padding:2B*3 (total 16 bytes each bbox)
    # ...

    roi_num = int(int.from_bytes(roi_bytes[0:2], byteorder='little') / 16)
    npa = np.zeros(shape=(1, roi_num, 4), dtype=np.int32)
    for i in range(roi_num):
        data = np.fromstring(
            roi_bytes[16 * (i + 1):16 * (i + 1) + 8], dtype=np.int16)
        npa[0, i, :] = data.astype(np.int32)
    return npa


def roi_nparray_to_binary(roi_np):
    """Convert ndarray to binary"""
    # box number:2B padding 2B*7   (total 16 bytes for header)
    # left:2B top:2B right:2B bottom:2B score:1B label:1B padding:2B*3 (total 16 bytes each bbox)
    # ...

    roi_num = roi_np.shape[1]
    res_bytes = np.array([roi_num * 16, 0, 0, 0, 0, 0, 0, 0],
                         dtype=np.uint16).tobytes()
    for i in range(roi_num):
        res_bytes += roi_np[0][i].astype(np.int16).tobytes()  # 2B*4
        res_bytes += np.array([0, 0, 0, 0],
                              dtype=np.int16).tobytes()  # 1B + 1B + 2B*3
    return res_bytes


def parse_input_number_from_stride_list(s):
    if s[0] != '[' or s[-1] != ']':
        print('stride list string error: ' + s)
        sys.exit(-1)
    ss = s[1:-2]
    lst = ss.split(',')
    return len(lst)


def create_random_roi(roi_num,
                      middle_layer_id,
                      base_image_scale,
                      input_feature_num,
                      is_legacy_roi=True,
                      is_fpn_roiresize=False):
    """Create random roi"""
    random.seed(227)
    max_area = input_feature_num * [0]
    for i in range(input_feature_num):
        max_area[i] = 16 * math.floor(
            math.pow(
                2, 2 *
                (i + 1 - middle_layer_id + math.log(base_image_scale, 2))))
        # print('max area ', i, " = ", max_area[i])

    roi_num_per_input = math.ceil(roi_num / input_feature_num)
    rois = []
    for i in range(input_feature_num):
        s_min = 0
        if i > 0:
            s_min = max_area[i - 1]
        s_max = max_area[i]
        h_max = math.floor(math.sqrt(s_max / 2))
        h_min = math.floor(math.sqrt(s_min / 2)) if s_min > 0 else 0
        w_max = math.floor(s_max / h_max)
        w_min = math.floor(s_min / h_min) if s_min > 0 else 0
        # print('Smin = ', Smin, 'Smax = ', Smax, 'Hmin = ', Hmin, 'Hmax =', Hmax, 'Wmin = ', Wmin, 'Wmax=', Wmax)
        for _ in range(roi_num_per_input):
            width = random.choice(range(w_min, w_max))
            height = random.choice(range(h_min, h_max))
            if is_fpn_roiresize:
                width = width // 2
                height = height // 2
            left = random.choice(
                range(1) if width < 8 else range(int(width / 8)))
            top = random.choice(
                range(1) if height < 8 else range(int(height / 8)))
            right = left + width
            bottom = top + height
            if is_legacy_roi:
                rois.append([left, top, right, bottom])
            else:
                rois.append([left, top, width, height])

    rois = rois[0:roi_num]
    np.random.shuffle(rois)
    rois_np = np.array(rois).reshape([roi_num, 4])
    return rois_np


def gen_random_rois(output_symbols, shape, tensor_name):
    """
    :param output_symbols: all symbols in model
    :param shape: roi shape
    :param tensor_name: name of roi tensor
    :return: roi data (numpy arrays)
    """

    for symbol in output_symbols.get_internals():
        op = symbol.attr('op_type_name')
        if op not in ('RoiAlign_X2', 'AlphaFPNROIResize'):
            continue

        s = symbol
        if op == 'RoiAlign_X2':
            if s.attr('feature_map_resize_mode') == 'True':
                continue

        input_names, _, _ = _get_inputs_outputs_shifts(s)

        # input tensors = input features + optional 'nop_weight' + rois
        if op == 'RoiAlign_X2':
            input_arguments = [
                x for x in input_names if x in s.list_arguments()
            ]
            nop_weights = [x for x in input_arguments if 'nop_weight' in x]
            rois = [x for x in input_arguments if not 'nop_weight' in x]
            assert len(rois) == 1
            rois_name = rois[0]
            if tensor_name and tensor_name != rois_name:
                continue
        else:  # FPNRoiResize
            rois = [input_names[0]]
            assert len(rois) == 1
            rois_name = rois[0]

        if op == 'RoiAlign_X2':
            middle_layer_id = int(s.attr('middle_layer_id'))
        else:
            middle_layer_id = int(s.attr('base_feat_id'))

        base_image_scale = 224
        if op == 'RoiAlign_X2':
            base_image_scale = int(s.attr('base_image_scale'))

        if op == 'RoiAlign_X2':
            input_h_stride_list = s.attr('feature_stride_h_list')
            input_feature_num = parse_input_number_from_stride_list(
                input_h_stride_list)
        else:
            spatial_scale = s.attr('spatial_scale')
            input_feature_num = parse_input_number_from_stride_list(
                spatial_scale)

        if op == 'RoiAlign_X2':
            assert input_feature_num == 5 - len(nop_weights)
        roi_num = shape[-2]
        roi_data = create_random_roi(
            roi_num, middle_layer_id, base_image_scale, input_feature_num,
            s.attr('legacy_roi') == 'True' if s.attr('legacy_roi') else True,
            op == 'AlphaFPNROIResize')

        return roi_data
    return None


def get_random_numpy_array(dtype, size, low=None, high=None):
    """
    :param dtype: numpy dtype
    :param size: numpy size tuple
    :return: random numpy ndarray
    """
    if dtype == 'float32':
        return np.random.rand(*size).astype(np.dtype(dtype))
    if low is None:
        low = np.iinfo(dtype).min
    if high is None:
        high = np.iinfo(dtype).max
    return np.random.randint(low=low, high=high, size=size, dtype=dtype)


def get_input_numpy_arrays(options, model_float_input_names,
                           model_extra_input_names, input_shifts_scales,
                           model_input_types, quant_by_scale, output_symbols):
    """
    :param model_extra_input_names:
    :param options: system arguments of this script
    :param model_float_input_names: model input names
    :param input_shifts_scales: input shifts or scales
    :param model_input_types: model input types
    :param quant_by_scale: quanti by scale or not
    :param output_symbols: all symbols in model
    :return: a list of numpy arrays
    """
    assert len(model_float_input_names) + len(model_extra_input_names) == len(
        options['shape'])

    results = []

    random.seed(216)
    generate_input = options['gen_random_input_and_exit']
    roi_input_index = None
    if 'roi_index' in options:
        roi_input_index = options['roi_index']

    if generate_input and len(input_shifts_scales) != len(
            model_float_input_names):
        # No param at this point
        if quant_by_scale:
            input_shifts_scales = [1 for x in model_float_input_names]
        else:
            input_shifts_scales = [0 for x in model_float_input_names]
    else:
        assert len(model_float_input_names) + len(
            model_extra_input_names) == len(input_shifts_scales)

    is_fpn_roiresize = False
    is_legacy_roi = False
    for symbol in output_symbols.get_internals():
        op = symbol.attr('op_type_name')
        if op == 'AlphaFPNROIResize':
            is_fpn_roiresize = True
            if symbol.attr('legacy_roi') == "1" or symbol.attr(
                    'legacy_roi') == "True":
                is_legacy_roi = True
            break

    # input_shifts and input_scales are exclusive
    roi_acc_id = 0
    for input_index, shape in enumerate(options['shape']):
        binary_file_name = options['input_binary'][input_index]
        tensor_name = options['input_name'][input_index]

        if not binary_file_name:
            a = get_random_numpy_array(np.int8, shape)
            continue
        type_or_shift_index = -1
        for fi_i, float_name in enumerate(model_float_input_names):
            if float_name == tensor_name:
                type_or_shift_index = fi_i
                break
        if type_or_shift_index == -1:
            dtype = np.dtype(model_input_types[input_index])
            shift_scale = input_shifts_scales[input_index]
        else:
            dtype = np.dtype(model_input_types[type_or_shift_index])
            shift_scale = input_shifts_scales[type_or_shift_index]
        if generate_input and binary_file_name:
            if roi_input_index is not None and input_index in roi_input_index:
                a = gen_random_rois(output_symbols, shape, tensor_name)
                assert a is not None
                if options['roi_pad_n'][roi_acc_id] < 0:
                    a = a[0:len(a) + options['roi_pad_n'][roi_acc_id]]
                elif options['roi_pad_n'][roi_acc_id] > 0:
                    for _ in range(options['roi_pad_n'][roi_acc_id]):
                        a = np.append(a, [[-1, -1, -1, -1]], axis=0)
                if is_fpn_roiresize:
                    a.astype(np.int32).tofile(binary_file_name)
                else:
                    a.astype(np.int16).tofile(binary_file_name)
                roi_acc_id = roi_acc_id + 1
                # roi_binary = roi_nparray_to_binary(a)
                # silent_remove_file(binary_file_name)
                # with open(binary_file_name, "wb") as f:
                #    f.write(roi_binary)
            elif dtype.itemsize >= 4:
                # float only has 24bit precision:
                # If input shift is small, needs to generate smaller input.
                # This is for LUT operator limitation.
                a = get_random_numpy_array(
                    dtype,
                    shape,
                    low=-(1 << (16 + min(int(shift_scale), 8))) + 1,
                    high=(1 << (16 + min(int(shift_scale), 8))) - 1)
                silent_remove_file(binary_file_name)
                with open(binary_file_name, 'wb') as f:
                    a.tofile(f)
            else:
                a = get_random_numpy_array(dtype, shape)
                silent_remove_file(binary_file_name)
                with open(binary_file_name, 'wb') as f:
                    a.tofile(f)

            # float32 numpy array
            unquant_scales = shift_scale if quant_by_scale else (
                float)(1 << int(shift_scale))
            a = a.astype(np.float32)
            npa = a / unquant_scales
            results.append(npa)
        else:
            n = 1
            for x in shape:
                n *= x

            if binary_file_name.find("_uint8_") != -1:
                assert dtype == np.dtype('int8')
                with open(binary_file_name, 'rb') as f:
                    a = np.fromfile(f, count=n, dtype=np.uint8)
                    a = a.reshape(shape)
                a = (a + np.iinfo(dtype).min).astype(dtype)
                # float32 numpy array
                unquant_scales = shift_scale if quant_by_scale else (
                    float)(1 << int(shift_scale))
                a = a.astype(np.float32)
                npa = a / unquant_scales
                results.append(npa)
            elif '_int8_' in binary_file_name:  # int8 values in binary file, should minus 128
                with open(binary_file_name, 'rb') as f:
                    a = np.fromfile(f, count=n, dtype=dtype)
                    a = a.reshape(shape)
                # float32 numpy array
                unquant_scales = shift_scale if quant_by_scale else (
                    float)(1 << int(shift_scale))
                a = a.astype(np.float32)
                npa = a / unquant_scales
                results.append(npa)
            elif (roi_input_index is not None) and (input_index in roi_input_index) \
                    and ((not is_fpn_roiresize) or is_legacy_roi):
                npa = np.fromfile(binary_file_name, dtype=np.int16)
                npa = npa.astype(np.int32)
                model_max_roi_num = shape[-2]
                per_roi_size = int(np.prod(shape) / model_max_roi_num)
                assert per_roi_size == 4, "roi size != 4?"
                assert len(npa) % (np.prod(shape) / model_max_roi_num) == 0, "roi input file length is not aligned to " \
                                                                             "each roi byte size"
                file_roi_num = int(
                    len(npa) / (np.prod(shape) / model_max_roi_num))
                if file_roi_num > model_max_roi_num:
                    npa = npa[0:model_max_roi_num * per_roi_size]
                elif file_roi_num < model_max_roi_num:
                    for _ in range(
                            per_roi_size * (model_max_roi_num - file_roi_num)):
                        npa = np.append(npa, np.int32(-1))
                npa = npa.reshape(shape)
                if (is_fpn_roiresize and is_legacy_roi):
                    # need float roi
                    npa = npa.astype(np.float32) / 4.0
                results.append(npa)
            else:
                with open(binary_file_name, 'rb') as f:
                    a = np.fromfile(f, count=n, dtype=dtype)
                    a = a.reshape(shape)
                # float32 numpy array
                unquant_scales = shift_scale if quant_by_scale else (
                    float)(1 << int(shift_scale))
                a = a.astype(np.float32)
                npa = a / unquant_scales
                results.append(npa)
    return tuple(results)


def _get_element(l, list_size_or_sizes, get_index):
    if not isinstance(list_size_or_sizes, (list, tuple)):
        list_size_or_sizes = tuple([list_size_or_sizes])
    if len(l) not in list_size_or_sizes:
        print('list should have %s items, but %d, details:' %
              (list_size_or_sizes, len(l)))
        pprint.pprint(l)
        sys.exit(1)
    return l[get_index]


def _get_inputs_outputs_shifts(s):
    """
    Return the input, output and shift names
    :param s:
    :return:
    """

    # output tensor name
    my_output_names = s.list_outputs()

    # input tensor name
    my_input_names = my_shift_names = []
    if s.get_children():
        all_shift_names = s.list_auxiliary_states()
        my_nodes = s.get_children().list_outputs()
        my_input_names = [x for x in my_nodes if x not in all_shift_names]

        # to-be-generated shift names
        my_shift_names = [x for x in my_nodes if x in all_shift_names]

    return my_input_names, my_output_names, my_shift_names


def index_of_input(input_name, options):
    for idx, in_name in enumerate(options['input_name']):
        if in_name == input_name:
            return idx

    return None


def infer_shape(options, all_symbols, all_symbols_tuple):
    """
    infer symbols' shapes
    :param options:
    :return:
    """

    all_shapes = dict()
    input_index = 0

    mxnet_inputs_params = all_symbols.list_arguments()

    for symbol in all_symbols_tuple:
        op = symbol.attr('op_type_name')
        name = symbol.attr('name')
        if op in ('QuantiInput', 'SQuantiInput'):
            data_name = symbol.get_children().list_outputs()[0]
            if symbol.list_arguments()[0] in mxnet_inputs_params:
                assert input_index < len(options['shape'])
                if options['input_name'][0]:
                    input_index = index_of_input(data_name, options)
                all_shapes[data_name] = options['shape'][input_index]
                if not options['input_name'][0]:
                    input_index += 1
        elif op == 'DetectionPostProcessing_X2' and symbol.attr(
                'image_size_fixed') == "False":
            data_name = symbol.list_arguments()[-1]
            if options['input_name'][0]:
                input_index = index_of_input(data_name, options)
            all_shapes[data_name] = (options['shape'][input_index][0],
                                     options['shape'][input_index][-1])
            if not options['input_name'][0]:
                input_index += 1
        elif op == 'null' and '_rois_' in name:
            if options['input_name'][0]:
                input_index = index_of_input(name, options)
            all_shapes[name] = options['shape'][input_index]
            if not options['input_name'][0]:
                input_index += 1

    # assert input_index == len(options['shape']), \
    #     "The actual number of input %d does not" \
    #     " equal to number of inputs in options %d" \
    #     % (input_index, len(options['shape']))

    shapes_by_type = all_symbols.infer_shape(**all_shapes)
    if shapes_by_type[1] is None:
        print('infer_shape failed')
        sys.exit(1)
    names_by_type = (all_symbols.list_arguments(), all_symbols.list_outputs(),
                     all_symbols.list_auxiliary_states())

    for names, shapes in zip(names_by_type, shapes_by_type):
        assert len(names) == len(shapes)
        for iname, ishape in zip(names, shapes):
            if iname in all_shapes:
                assert all_shapes[iname] == ishape
            else:
                all_shapes[iname] = ishape
    options['all_shapes'] = all_shapes

    if options['debug'] > 1:
        for iname in all_shapes:
            print(iname, 'shape is', all_shapes[iname])


def propagate_feature_shift_until_stable(options, all_symbols_tuple,
                                         feature_shift, feature_shift_range,
                                         gen_one_random):
    """
    propagate constrained feature shift until stable.
    If gen_one_random is True, generate shift for exactly one concat of split,
    and propagate until stable
    """

    def update(d, k, v):
        if k not in d:
            d[k] = v
        else:
            assert d[k] == v

    def process_one_symbol(s, feature_shift, feature_shift_range,
                           gen_one_random, has_unhandled_constraint):
        """
        process one symbol, update "feature_shift"
        return "gen_one_random" and "has_unhandled_constraint"
        """
        op = s.attr('op_type_name')
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        input_features = [
            x for x in input_names if x not in s.list_arguments()
        ]

        if op == 'QuantiInput':  # may specify output shift
            otname = _get_element(output_names, 1, 0)
            if s.attr('fixed_output_shift'):
                shift = int(s.attr('fixed_output_shift'))
                update(feature_shift, otname, shift)
        elif op == 'QuantiChannelSum':  # may specify output shift
            otname = _get_element(output_names, 1, 0)
            if s.attr('out_shift'):
                shift = int(s.attr('out_shift'))
                update(feature_shift, otname, shift)
        elif op == 'DetectionPostProcessing_X2':  # specify input shift
            if s.attr('input_shift'):
                shift = int(s.attr('input_shift'))
                for itname in input_features:
                    update(feature_shift, itname, shift)
        elif op == "MulAdd":
            otname = _get_element(output_names, 1, 0)
            if s.attr('out_shift'):
                shift = int(s.attr('out_shift'))
                if shift >= 0:
                    update(feature_shift, otname, shift)
        elif op in ['AlphaPooling', 'QuantiShuffle'
                    ] or (op == 'RoiAlign_X2'
                          and s.attr('feature_map_resize_mode') == 'True'):
            # input and output shift must be the same
            itname = _get_element(input_names, 1, 0)
            otname = _get_element(output_names, 1, 0)
            if itname in feature_shift and otname in feature_shift:
                assert feature_shift[itname] == feature_shift[otname]
            elif itname in feature_shift:
                feature_shift[otname] = feature_shift[itname]
            elif otname in feature_shift:
                feature_shift[itname] = feature_shift[otname]
            elif gen_one_random:
                feature_shift[itname] = feature_shift[otname] = 7
                gen_one_random = False
            else:
                has_unhandled_constraint = True
        elif op == 'RoiAlign_X2':
            for input_index in range(5):
                itname = _get_element(input_names, 6, input_index)
                otname = _get_element(output_names, 1, 0)
                if itname in feature_shift:
                    feature_shift[otname] = feature_shift[itname]
                if otname in feature_shift:
                    feature_shift[itname] = feature_shift[otname]
            itname = _get_element(input_names, 6, 5)
            update(feature_shift, itname, 0)

        elif op in ('Concat', 'SliceChannel'):
            # all input shifts must be the same
            assert not shift_names

            shift = None
            for tname in input_names + output_names:
                if tname in feature_shift:
                    assert shift is None or shift == feature_shift[tname]
                    shift = feature_shift[tname]

            if shift is None and gen_one_random:
                shift = random.randrange(*feature_shift_range)
                gen_one_random = False

            if shift is not None:
                for tname in input_names + output_names:
                    update(feature_shift, tname, shift)
            else:
                has_unhandled_constraint = True
        elif op == 'AlphaWarp':
            map_tname = _get_element(input_names, 2, 1)
            if map_tname not in feature_shift:  # [0, 8]
                update(feature_shift, map_tname, random.randrange(0, 9))
        elif op == 'AlphaResize':
            shift = None
            if output_names[0] in feature_shift:
                assert shift is None or shift == feature_shift[output_names[0]]
                shift = feature_shift[output_names[0]]

            if shift is not None:
                for tname in input_names + output_names:
                    if tname not in feature_shift:
                        has_unhandled_constraint = True
                        break
                for tname in input_names + output_names:
                    update(feature_shift, tname, shift)
        elif op == 'QuantiCorrelation':
            otname = _get_element(output_names, 1, 0)
            if s.attr('output_shift'):
                shift = int(s.attr('output_shift'))
                if output_names[0] in feature_shift:
                    assert shift in (0, feature_shift[output_names[0]])
                update(feature_shift, otname, shift)

        return gen_one_random, has_unhandled_constraint

    while True:
        old_size = len(feature_shift)
        has_unhandled_constraint = False

        start = time.time()

        for s in all_symbols_tuple:
            gen_one_random, has_unhandled_constraint = process_one_symbol(
                s, feature_shift, feature_shift_range, gen_one_random,
                has_unhandled_constraint)

        if options['debug'] > 0:
            elapsed_time = float(time.time() - start)
            if options['debug'] > 1 or elapsed_time > 1:
                print('cost_time=%.3f, a round of shift propagation' %
                      float(elapsed_time))

        new_size = len(feature_shift)
        if old_size == new_size:  # stable
            return has_unhandled_constraint


def get_param(options, all_symbols_tuple):
    """
    load param if file exist, or generate a random one
    :param options:
    :return:
    """

    if not options['gen_random_param_and_exit']:
        if os.path.isfile(options['param']):
            return mxnet.nd.load(options['param'])
        print('cannot open %s for reading' % options['param'], file=sys.stderr)
        sys.exit(1)

    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print(
            'elapsed_time=%.3f, start shift propagation' % float(elapsed_time))

    # pre-determine constrained feature shift, e.g., concat, dpp
    random.seed(216)
    feature_shift_range = (
        7, 10)  # 7, 8, 9 (Add 4 for int16 input, Add 12 for int32 input)
    special_shift = dict()
    propagate_feature_shift_until_stable(options, all_symbols_tuple,
                                         special_shift, None, False)
    while propagate_feature_shift_until_stable(options, all_symbols_tuple,
                                               special_shift,
                                               feature_shift_range, True):
        pass

    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print(
            'elapsed_time=%.3f, after shift propagation' % float(elapsed_time))

    choice_weight = [abs(x - 128) / 10.0 for x in range(256)]  # 'v' shape
    choice_weight = [128 - x for x in choice_weight]  # '^' shape
    choice_weight[128] = 1  # low chance to select 0
    choice_weight = tuple(x**10 for x in choice_weight)
    # print(choice_weight)
    choice_weight = np.array(choice_weight, dtype=np.float)
    choice_weight /= np.sum(choice_weight)  # sum to 1

    sname_shifts = dict()  # name (conv0_bias_shift_history) to int8 list
    tname_shifts = dict()  # name (conv0_bias) to int8 list, more than in param
    tname_data = dict()  # name (conv0_bias) to NDArray
    aux_data = dict()  # Auxilary node name to NDArray

    def query_or_random(tname, special_tname_shift, feature_shift_range):
        if tname in special_tname_shift:
            return special_tname_shift[tname]
        return random.randrange(*feature_shift_range)

    def rand_quantiinput(s):
        otname = _get_element(s.list_outputs(), 1, 0)
        shifts = [query_or_random(otname, special_shift, feature_shift_range)]
        if s.attr('fixed_output_shift'):  # specified in json
            assert shifts == [int(s.attr('fixed_output_shift'))]
        if s.attr('out_type') == 'int16':
            shifts = [x + 4 for x in shifts]
        elif s.attr('out_type') == 'int32':
            shifts = [x + 12 for x in shifts]
        osname = _get_element(s.list_auxiliary_states(), 1, 0)
        sname_shifts[osname] = tname_shifts[otname] = shifts

        if options['debug'] > 1:
            print(osname, '=', sname_shifts[osname])

    def rand_squantiinput(s):
        # scale = [1 / random.uniform(0.25 / 127, 2 / 127)]
        scale = [1 / 76]
        osname = _get_element(s.list_auxiliary_states(), 1, 0)
        # sname_shifts[osname] = tname_shifts[otname] = scale
        aux_data[osname] = mxnet.nd.array(scale, dtype=np.float32)

    def pass_on_first_input_shift(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        if not shift_names and not sname_shifts:
            return  # in squanization model, snames and tnames should be empty!!!
        assert not shift_names
        ishift_0 = _get_element(tname_shifts[input_names[0]], 1, 0)
        tname_shifts[output_names[0]] = [ishift_0]
        if options['debug'] > 1:
            print(output_names[0], '=', tname_shifts[output_names[0]],
                  " (absent in param file)")

    def pass_on_second_input_shift(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        if not shift_names and not sname_shifts:
            return  # in squanization model, snames and tnames should be empty!!!
        assert not shift_names
        ishift_0 = _get_element(tname_shifts[input_names[1]], 1, 0)
        tname_shifts[output_names[0]] = [ishift_0]
        if options['debug'] > 1:
            print(output_names[0], '=', tname_shifts[output_names[0]],
                  " (absent in param file)")

    def pass_on_shift(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        if not shift_names and not sname_shifts:
            return  # in squanization model, snames and tnames should be empty!!!
        assert not shift_names

        try:
            ishift_0 = _get_element(tname_shifts[input_names[0]], 1, 0)
            tname_shifts[output_names[0]] = [ishift_0]
        except (
                KeyError, IndexError
        ):  # TODO: quick, bad and lazy bug fix for RcnnPostProcess random param gen
            tname_shifts[output_names[0]] = [0]

        if options['debug'] > 1:
            print(output_names[0], '=', tname_shifts[output_names[0]],
                  " (absent in param file)")

    def check_predefined_shift(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        if not shift_names and not sname_shifts:
            return  # in squanization model, snames and tnames should be empty!!!
        assert not shift_names
        ishift_0 = _get_element(tname_shifts[input_names[0]], 1, 0)
        for tname in input_names + output_names:
            assert special_shift[tname] == ishift_0
            if tname in input_names:
                assert tname_shifts[tname] == [ishift_0]
            else:
                tname_shifts[tname] = [ishift_0]
                if options['debug'] > 1:
                    print(tname, '=', tname_shifts[tname],
                          " (absent in param file)")

    def rand_softmaxoutput(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        assert len(input_names) == 2  # input and softmax_label
        assert len(output_names) == 1
        assert not shift_names
        # output is float, so no shift

    def rand_binary_no_shift(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        assert len(input_names) == 2  # atname, btname
        assert not tname_shifts or tname_shifts[
            input_names[0]] == tname_shifts[input_names[1]]
        assert len(output_names) == 1
        assert not shift_names
        # no shift for cmp

    def rand_elementwise(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        otname = _get_element(output_names, 1, 0)

        # query by tname, and set sname
        if s.attr('mode') == 'normal':
            assert len(input_names) == 3  # atname, btname, ctname
            assert len(shift_names) == 4  # asname, bsname, osname, csname
            a_b_names = input_names[:2]
            input_names.insert(2, otname)
        elif s.attr('mode') == 'mul':
            assert len(input_names) == 2  # atname, btname
            assert len(shift_names) == 3  # asname, bsname, osname
            a_b_names = input_names[:2]
            input_names.insert(2, otname)
        elif s.attr('mode') in ('add', 'neg_add'):
            assert len(input_names) == 3  # atname, dummy_b_name, ctname
            assert len(shift_names) == 4  # asname, bsname, osname, csname
            a_b_names = input_names[:1]
            input_names.insert(2, otname)

            # TODO: hack, generate 'arg:muladd0_data_b'
            # NOTE: sometimes the name does not contain 'muladd0'
            b_name = s.attr('name') + '_data_b'
            if b_name in options['all_shapes']:
                b_shape = options['all_shapes'][b_name]
            else:
                b_name = s.attr(
                    'name')[0:s.attr('name').rfind('_')] + '_data_b'
                b_shape = options['all_shapes'][b_name]
            b_size = functools.reduce(operator.mul, b_shape, 1)
            b_data = mxnet.nd.array(
                [1] * b_size, dtype=np.int8).reshape(b_shape)
            tname_data[b_name] = b_data
        else:
            assert False, 'unsupported MulAdd mode %s' % s.attr('mode')

        # element-wise output only supports right shift (as + bs - os >= 0)
        max_os = sum([tname_shifts[x][0] for x in a_b_names])
        max_os = min(max_os, feature_shift_range[1])
        assert feature_shift_range[0] <= max_os
        tname_shifts[otname] = [
            query_or_random(otname, special_shift,
                            [feature_shift_range[0], max_os + 1])
        ]

        for (tname, sname) in zip(input_names, shift_names):
            v = tname_shifts.get(tname, [0])
            sname_shifts[sname] = v * options['all_shapes'][sname][0]

        if options['debug'] > 1:
            for sname in shift_names:
                print(sname, '=', sname_shifts[sname])

    int4_features = []

    def rand_conv(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        otname = _get_element(output_names, 1, 0)

        # input tensor names
        assert len(input_names) in (2, 3, 4)
        iname = input_names[0]
        wname = input_names[1]
        sname = input_names[3] if len(input_names) == 4 else None

        # to-be-generated shift names
        osname = shift_names[0]
        wsname = shift_names[1]
        is_deconv = s.attr('op_type_name') == 'QuantiDeconvolution'
        if is_deconv:
            osname = shift_names[1]
            wsname = shift_names[0]

        if s.attr('out_type') in ('int4', 'uint4'):
            int4_features.append(otname)

        # generate output shift
        oshift_size = _get_element(options['all_shapes'][osname], 1, 0)
        oshift = [query_or_random(otname, special_shift, feature_shift_range)
                  ] * oshift_size

        oshift_0 = _get_element(oshift, 1, 0)
        if s.attr('disable_output_quantization') == 'True':
            oshift = [0]
        sname_shifts[osname] = tname_shifts[otname] = oshift
        if options['debug'] > 1:
            print(osname, '=', sname_shifts[osname])

        # determine weight shift range
        ishift_0 = _get_element(tname_shifts[iname], 1, 0)
        # 0 <= ishift + wshift - oshift < 32, BPU constraint, but use 16
        temps = [oshift_0 - ishift_0]
        if sname:  # 0 <= ishift + wshift - sshift < 16, BPU constraint
            temps += [_get_element(tname_shifts[sname], 1, 0) - ishift_0]
        wshift_min = max(0, max(temps))
        wshift_max = min(16, min(temps) + 16)

        # select a good weight shift
        wshape = options['all_shapes'][wname]
        wsize = functools.reduce(operator.mul, wshape, 1)
        wsize_per_k = wsize / _get_element(wshape, 4, 0)
        # wsize_per_k is in the range of [9, 7*7*2048], almost [10^1, 10^5]
        # for small kernel, we should keep the sum in a small range,
        # and give them small shift values.
        # thus we prefer right shift [6, 8], for 10^[1, 5] respectively
        rshift_min = math.floor(math.log(wsize_per_k, 10) / 2) + 6
        rshift_max = math.ceil(math.log(wsize_per_k + 1, 10) / 2) + 6
        # right_shift = ishift + wshift - oshift
        while True:
            try_wshift_min = max(wshift_min, rshift_min + oshift_0 - ishift_0)
            try_wshift_max = min(wshift_max, rshift_max + oshift_0 - ishift_0)
            if try_wshift_min < try_wshift_max:
                wshift_min = try_wshift_min
                wshift_max = try_wshift_max
                break
            else:
                rshift_min -= 1
                rshift_max += 1

        # generate weight shift
        wshift_size = _get_element(options['all_shapes'][wsname], 1, 0)
        if wshift_min + 1 == wshift_max:
            wshift = np.array([wshift_min] * wshift_size)
        else:
            wshift = np.random.randint(
                low=wshift_min, high=wshift_max - 1, size=wshift_size)
        if os.getenv('FUSA_COMP_EN', 'null') == '1' and wshift_size != 1:
            for i in range(math.ceil(wshift_size / 16)):
                cend = min((i + 1) * 16, wshift_size)
                wshift[i * 16:cend] = [wshift[i * 16]] * (cend - i * 16)
        sname_shifts[wsname] = tname_shifts[wname] = wshift
        if options['debug'] > 1:
            print(wsname, '=', sname_shifts[wsname])

        # generate weight data for each shift
        weight_sparsity = [1, 1]
        if options['weight_sparsity']:
            splited_str = options['weight_sparsity'].split('/', 1)
            assert len(splited_str) == 2
            weight_sparsity[0] = int(splited_str[0])
            weight_sparsity[1] = int(splited_str[1])
            assert weight_sparsity[0] > 0 \
                   and weight_sparsity[0] <= weight_sparsity[1]

        if input_names[0] in int4_features:
            # 4-bit feature uses int4 weight
            arr_i8 = np.array([x if x < 8 else x - 16 for x in range(16)] * 16)
        else:  # 8-bit feature uses int8 weight
            arr_i8 = np.array(range(-128, 128))

        if weight_sparsity[0] == weight_sparsity[1]:  # dense weight
            if options['complement_weight']:
                wdata = np.zeros(shape=(wsize // wshape[3], wshape[3]))
                # generate weight for first 1x1x1xC
                wdata[0] = np.random.choice(
                    arr_i8, size=wshape[3], p=choice_weight)
                # complement weight for other 1x1x1xC
                for i in range(1, wsize // wshape[3]):
                    for j in range(wshape[3]):
                        wdata[i][j] = -wdata[i - 1][j] - 1
            else:
                wdata = np.zeros(shape=(wshift_size, wsize // wshift_size))
                for i in range(wshift_size):
                    # rshift = ishift_0 + wshift[i] - oshift_0  # [4, 8]
                    # larger shift need more 'flat' distribution
                    # cw = tuple(x**(12 - rshift) for x in choice_weight)
                    wdata[i] = np.random.choice(
                        arr_i8, size=wsize // wshift_size, p=choice_weight)
        else:  # sparse weight
            wdata = np.zeros(shape=(wsize,))
            widx = 0
            for _ in range(wsize // wshape[3]):
                for ci in range(0, wshape[3], weight_sparsity[1]):
                    cend = min(ci + weight_sparsity[1], wshape[3])
                    one_kernel = np.random.choice(
                        arr_i8, size=weight_sparsity[0], p=choice_weight)
                    one_kernel = np.append(
                        one_kernel,
                        [0] * (weight_sparsity[1] - weight_sparsity[0]))
                    np.random.shuffle(one_kernel)
                    wdata[widx:widx + cend - ci] = one_kernel[:cend - ci]
                    widx += cend - ci

        if os.getenv('FUSA_COMP_EN', 'null') == '1':
            wdata = wdata.flatten()
            for i in range(math.ceil(wshape[0] / 16)):
                kstart = i * 16
                kend = min(wshape[0], (i + 1) * 16)
                dstart = kstart * wsize // wshape[0]
                wdata[dstart:kend * wsize // wshape[0]] = np.tile(
                    wdata[dstart:dstart + wsize // wshape[0]], kend - kstart)
        wdata = mxnet.nd.array(wdata, dtype=np.int8).reshape(wshape)
        tname_data[wname] = wdata

        has_bias = s.attr('no_bias') == 'False' or not s.attr('no_bias')
        if has_bias:
            bname = input_names[2]
            bsname = shift_names[2]
            # generate bias values
            bshape = options['all_shapes'][bname]
            bsize = functools.reduce(operator.mul, bshape, 1)
            bdata_list = np.random.choice(arr_i8, size=bsize, p=choice_weight)

            # generate bias shift
            bshift_size = _get_element(options['all_shapes'][bsname], 1, 0)
            assert wshift_size == bshift_size
            bshift = []
            for i in range(bshift_size):
                temp = ishift_0 + wshift[i]
                if sname is None and options['large_bias']:
                    # if no sumin, and the bias value is more than int8,
                    # we can distribute a part of bias to sumin
                    # For example 0x723 << 10 = (0x72 << 12) + (0x3 << 10)
                    # in order to test this feature, we generate 2 int8
                    # values using max & min shift, and merge them

                    temp = ishift_0 + wshift[i]
                    shift1 = max(
                        0, temp - 15)  # inclusive, smallest shift, small value
                    shift2 = min(16,
                                 temp)  # inclusive, largest shift, large value
                    shift2 = random.randrange(
                        max(shift1, shift2 - 2), shift2 + 1)
                    bshift.append(shift2)

                    start, end = (0, bsize) if bshift_size == 1 else (i, i + 1)
                    for j in range(start, end):
                        # overwrite bias value(s)
                        value1 = bdata_list[j]
                        value2 = random.randrange(-128, 127)
                        bdata_list[j] = value1 * 2**(shift2 - shift1) + value2
                else:  # has sumin, use int8 bias
                    bvalue = abs(bdata_list[i])
                    # quantized output would be added by bvalue << (oshift - bshift)
                    # we want to keep this addend near 16
                    # bvalue * 2^(oshift - bshift) == 16
                    # bshift = oshift - log(16 / bvalue)
                    good_shift = oshift_0 - (
                        int(math.log(16 / bvalue, 2) if bvalue else 0))

                    # 0 <= ishift + wshift - bshift < 16, BPU constraint
                    bshift_min = max(0, good_shift - 3, temp - 15)
                    bshift_max = min(16, good_shift + 4, temp + 1)
                    bshift.append(random.randrange(bshift_min, bshift_max))

            bdata_type = np.int8 if all([-128 <= x <= 127
                                         for x in bdata_list]) else np.int32
            if os.getenv('FUSA_COMP_EN', 'null') == '1':
                for i in range(math.ceil(bsize / 16)):
                    cend = min((i + 1) * 16, bsize)
                    bdata_list[i * 16:cend] = [bdata_list[i * 16]
                                               ] * (cend - i * 16)
                if bshift_size != 1:
                    for i in range(math.ceil(bshift_size / 16)):
                        cend = min((i + 1) * 16, bshift_size)
                        bshift[i * 16:cend] = [bshift[i * 16]
                                               ] * (cend - i * 16)
            bdata = mxnet.nd.array(
                bdata_list, dtype=bdata_type).reshape(bshape)
            tname_data[bname] = bdata
            sname_shifts[bsname] = tname_shifts[bname] = bshift
            if options['debug'] > 1:
                print(bsname, '=', sname_shifts[bsname])

    def rand_sconv(s):
        input_output_names = _get_inputs_outputs_shifts(s)
        input_names = input_output_names[0]
        output_names = input_output_names[1]
        squanti_names = input_output_names[2]

        otname = _get_element(output_names, 1, 0)
        if s.attr('out_type') in ('int4', 'uint4'):
            int4_features.append(otname)
        # input tensor names
        assert len(input_names) in (2, 3, 4)

        def rand_choices_of_shifts(value_range,
                                   return_size,
                                   reverse_weight=False,
                                   exp=10):
            choice_values = np.array(range(*value_range))
            choice_weights = [x**exp for x in choice_values]
            choice_weights /= np.sum(choice_weights)
            if reverse_weight:
                choice_weights = choice_weights[::-1]
            return np.random.choice(
                choice_values, size=return_size, p=choice_weights)

        def modify_data_for_fusa_comp_mode(data, k, size):
            data = data.flatten()
            assert size % k == 0
            for i in range(math.ceil(k / 16)):
                kstart = i * 16
                kend = min(size, (i + 1) * 16)
                dstart = kstart * (size // k)
                data[dstart:kend * (size // k)] = np.tile(
                    data[dstart:dstart + size // k], kend - kstart)
            return data

        # fixed_bias_shift is not actually used by refc, so do not consider it!!
        name_idx = 0
        has_bias = s.attr('no_bias') == 'False' or not s.attr('no_bias')
        if has_bias:
            bshiftname = squanti_names[name_idx]
            bshift_size = _get_element(options['all_shapes'][bshiftname], 1, 0)
            bshift = rand_choices_of_shifts((0, 14), bshift_size, True, 5)
            if os.getenv('FUSA_COMP_EN', 'null') == '1':
                bshift = modify_data_for_fusa_comp_mode(
                    bshift, bshift_size, bshift_size)
            aux_data[bshiftname] = mxnet.nd.array(bshift, dtype=np.int8)
            name_idx += 1
        # disable_output_quantization = True. output feature will have a float scale
        if s.attr('disable_output_quantization') == 'True':
            coscalename = squanti_names[name_idx]
            coscale_size = _get_element(options['all_shapes'][coscalename], 1,
                                        0)
            coscale = np.random.uniform(
                0.25 / 127 / 127, 4 / 127 / 127, size=coscale_size)
            if os.getenv('FUSA_COMP_EN', 'null') == '1':
                coscale = modify_data_for_fusa_comp_mode(
                    coscale, coscale_size, coscale_size)
            aux_data[coscalename] = mxnet.nd.array(coscale, dtype=np.float32)
            name_idx += 1
        else:
            cscalename = squanti_names[name_idx]
            cscale_size = _get_element(options['all_shapes'][cscalename], 1, 0)
            cscale = np.random.randint(16384, 16384 * 2, size=cscale_size)
            if os.getenv('FUSA_COMP_EN', 'null') == '1':
                cscale = modify_data_for_fusa_comp_mode(
                    cscale, cscale_size, cscale_size)
            aux_data[cscalename] = mxnet.nd.array(cscale, dtype=np.int32)
            name_idx += 1

            crshiftname = squanti_names[name_idx]
            crshift_size = _get_element(options['all_shapes'][crshiftname], 1,
                                        0)
            crshift = rand_choices_of_shifts((1, 8), crshift_size, True, 2)
            if os.getenv('FUSA_COMP_EN', 'null') == '1':
                crshift = modify_data_for_fusa_comp_mode(
                    crshift, crshift_size, crshift_size)
            aux_data[crshiftname] = mxnet.nd.array(crshift, dtype=np.int8)
            name_idx += 1

            coshiftname = squanti_names[name_idx]
            coshift_size = _get_element(options['all_shapes'][coshiftname], 1,
                                        0)
            coshift = rand_choices_of_shifts((21, 24), coshift_size)
            if os.getenv('FUSA_COMP_EN', 'null') == '1':
                coshift = modify_data_for_fusa_comp_mode(
                    coshift, coshift_size, coshift_size)
            aux_data[coshiftname] = mxnet.nd.array(coshift, dtype=np.int8)
            name_idx += 1

        # generate elementwise scales and shifts
        if s.attr('elementwise_input') == 'True':
            escalename = squanti_names[name_idx]
            escale_size = _get_element(options['all_shapes'][escalename], 1, 0)
            escale = np.random.randint(16, 16384, size=escale_size)
            aux_data[escalename] = mxnet.nd.array(escale, dtype=np.int32)
            name_idx += 1

            eshiftname = squanti_names[name_idx]
            eshift_size = _get_element(options['all_shapes'][eshiftname], 1, 0)
            eshift = rand_choices_of_shifts((0, 2), eshift_size, True, 10)
            aux_data[eshiftname] = mxnet.nd.array(eshift, dtype=np.int8)
            name_idx += 1

        # generate weight data
        wname = input_names[1]
        wshape = options['all_shapes'][wname]
        wsize = functools.reduce(operator.mul, wshape, 1)
        weight_sparsity = [1, 1]
        if options['weight_sparsity']:
            splited_str = options['weight_sparsity'].split('/', 1)
            assert len(splited_str) == 2
            weight_sparsity[0] = int(splited_str[0])
            weight_sparsity[1] = int(splited_str[1])
            assert weight_sparsity[0] > 0 \
                   and weight_sparsity[0] <= weight_sparsity[1]

        if input_names[0] in int4_features:
            # 4-bit feature uses int4 weight
            arr_i8 = np.array([x if x < 8 else x - 16 for x in range(16)] * 16)
        else:  # 8-bit feature uses int8 weight
            arr_i8 = np.array(range(-128, 128))

        if weight_sparsity[0] == weight_sparsity[1]:
            wdata = np.random.choice(arr_i8, size=wsize, p=choice_weight)
        else:
            wdata = np.zeros(shape=(wsize))
            widx = 0
            for _ in range(wsize // wshape[3]):
                for ci in range(0, wshape[3], weight_sparsity[1]):
                    cend = min(ci + weight_sparsity[1], wshape[3])
                    one_kernel = np.random.choice(
                        arr_i8, size=weight_sparsity[0], p=choice_weight)
                    one_kernel = np.append(
                        one_kernel,
                        [0] * (weight_sparsity[1] - weight_sparsity[0]))
                    np.random.shuffle(one_kernel)
                    wdata[widx:widx + cend - ci] = one_kernel[:cend - ci]
                    widx += cend - ci
        if os.getenv('FUSA_COMP_EN', 'null') == '1':
            wdata = wdata.flatten()
            for i in range(math.ceil(wshape[0] / 16)):
                kstart = i * 16
                kend = min(wshape[0], (i + 1) * 16)
                dstart = kstart * wsize // wshape[0]
                wdata[dstart:kend * wsize // wshape[0]] = np.tile(
                    wdata[dstart:dstart + wsize // wshape[0]], kend - kstart)
        wdata = mxnet.nd.array(wdata, dtype=np.int8).reshape(wshape)
        tname_data[wname] = wdata

        # generate bias values, different from x2, x2a has int16 bias
        if has_bias:
            bname = input_names[2]
            bshape = options['all_shapes'][bname]
            bsize = functools.reduce(operator.mul, bshape, 1)
            bdata_list = np.random.choice(
                np.array(range(-16384, 16384)), size=bsize)
            if os.getenv('FUSA_COMP_EN', 'null') == '1':
                for i in range(math.ceil(bsize / 16)):
                    cend = min((i + 1) * 16, bsize)
                    bdata_list[i * 16:cend] = [bdata_list[i * 16]
                                               ] * (cend - i * 16)
            bdata = mxnet.nd.array(bdata_list, dtype=np.int32).reshape(bshape)
            tname_data[bname] = bdata

    def rand_dpp(s):
        input_names, _, shift_names = _get_inputs_outputs_shifts(s)
        assert not shift_names

        # input tensors = input features + optional 'nop_weight' + exp tables
        input_arguments = [x for x in input_names if x in s.list_arguments()]
        has_nop_weight = 'nop_weight' in input_arguments
        input_arguments = [x for x in input_arguments if not 'nop_weight' in x]
        assert len(input_arguments) == 3
        anchor_table, exp_table, im_info = input_arguments

        # attributes to generate tables
        exp_shift = int(s.attr('exp_output_shift'))  # not 'exp_shift'
        input_shift = int(s.attr('input_shift'))
        num_anchors = ast.literal_eval(s.attr('num_anchors'))
        feature_stride_h = ast.literal_eval(s.attr('feature_stride_h'))
        feature_stride_w = ast.literal_eval(s.attr('feature_stride_w'))

        # Default scales and ratios scale/ratio initializer is not provided
        scales = [[1] * sum(num_anchors)] * len(num_anchors)
        ratios = [[1] * sum(num_anchors)] * len(num_anchors)

        anchor_initializer = ""

        # Try to load from scales/ratios from the "__init__" attributes of
        # the anchor from the json file.
        if "__init__" in s.attr_dict()[input_arguments[0]]:
            anchor_initializer = s.attr_dict()[input_arguments[0]]["__init__"]
        if anchor_initializer:
            # init_data is similar to the following
            # ['anchortableinitializer',
            # {'feature_h_list': [8, 8], 'feature_w_list': [8, 8],
            # 'scales': [[1, 2], [1, 2]], 'ratios': [[1, 2], [1, 2]]}]
            init_data = json.loads(anchor_initializer)
            assert init_data[0] == 'anchortableinitializer'
            try:
                scales = init_data[1]['scales']
                ratios = init_data[1]['ratios']
            except (KeyError, NameError):
                pass

        # exp table
        exp_table_values = []
        initializer = ExpTableInitializer(16, exp_shift, 8, input_shift)
        initializer._init_default(  # pylint: disable=protected-access
            exp_table, exp_table_values)
        exp_table_values = [x.asnumpy() for x in exp_table_values]
        exp_table_values = mxnet.nd.array(exp_table_values, dtype=np.int32)
        exp_table_values = exp_table_values.reshape(tuple([256]))

        # anchor table
        anchor_table_values = []
        initializer = AnchorTableInitializer(feature_stride_h,
                                             feature_stride_w, scales, ratios)
        initializer._init_default(  # pylint: disable=protected-access
            anchor_table, anchor_table_values)
        anchor_table_values = [x.asnumpy() for x in anchor_table_values]
        anchor_table_values = mxnet.nd.array(
            anchor_table_values, dtype=np.int32)
        anchor_table_values = anchor_table_values.reshape((sum(num_anchors),
                                                           4))

        # im_info
        im_info_shape = options['all_shapes'][im_info]
        im_info_values = [0] * functools.reduce(operator.mul, im_info_shape, 1)
        im_info_values = mxnet.nd.array(im_info_values, dtype=np.float32)
        im_info_values = im_info_values.reshape(im_info_shape)

        tname_data[exp_table] = exp_table_values
        tname_data[anchor_table] = anchor_table_values
        tname_data[im_info] = im_info_values
        if has_nop_weight:
            options['all_shapes']['nop'] = tuple([1])
            tname_data['nop'] = mxnet.nd.array([0], dtype=np.int8)

        if options['debug'] > 1:
            print(exp_table, '=', exp_table_values)
            print(anchor_table, '=', anchor_table_values)
            print(im_info, '=', im_info_values)

    def pass_on_for_warp(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        assert not shift_names

        assert len(input_names) == 2
        assert len(output_names) == 1
        ishift_0 = _get_element(tname_shifts[input_names[0]], 1, 0)
        tname_shifts[output_names[0]] = [ishift_0]

        if options['debug'] > 1:
            print(output_names[0], '=', tname_shifts[output_names[0]],
                  " (absent in param file)")

    def rand_channelsum(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        assert len(input_names) == 1
        assert len(output_names) == 1
        otname = _get_element(output_names, 1, 0)
        osname = shift_names[1]

        input_shift = tname_shifts.get(input_names[0], [0])
        num_channel = options['all_shapes'][input_names[0]][-1]

        if otname in special_shift:  # already specified in json
            tname_shifts[otname] = [special_shift[otname]]
        elif s.attr('out_type') == 'int8':
            # sum is "num_channel" times larger at most
            tmp_exp = math.ceil(math.log(num_channel, 4))
            tname_shifts[otname] = [max(0, x - tmp_exp) for x in input_shift]
        elif s.attr('out_type') == 'int16' or s.attr('out_type') == 'int32':
            tname_shifts[otname] = input_shift
        else:
            assert False, 'unsupported ChannelSum output type %s' % s.attr(
                'out_type')

        sname_shifts[osname] = tname_shifts[otname]

        for (tname, sname) in zip(input_names, shift_names):
            v = tname_shifts.get(tname, [0])
            sname_shifts[sname] = v

        if options['debug'] > 1:
            for sname in shift_names:
                print(sname, '=', sname_shifts[sname])

    def handle_lut(s):
        attrs = s.list_attr()

        def lut_type_string_to_enum(lut_type: str) -> int:  # pylint: disable=R1710
            if lut_type == "exp":
                return lut.K_EXP
            if lut_type == "log":
                return lut.K_LOG
            if lut_type == "sigmoid":
                return lut.K_SIGMOID
            if lut_type == "tanh":
                return lut.K_TANH
            assert False, "unsupported lut type: " + str(lut_type)

        param = lut.LUTParam(
            lut_type=lut_type_string_to_enum(attrs['lut_type']),
            sparse_min=float(attrs['sparse_min']),
            sparse_max=float(attrs['sparse_max']),
            ymax=float('ymax' in attrs and attrs['ymax'] or 0),
            sparse_steps=int('sparse_steps' in attrs and attrs['sparse_steps']
                             or 256),
            dense_min=float(attrs['dense_min']),
            dense_max=float(attrs['dense_max']),
            x_min=float(attrs['x_min']),
            x_max=float(attrs['x_max']),
            idx_bits=int('idx_bits' in attrs and attrs['idx_bits'] or 4),
            data_shift=int('data_shift' in attrs and attrs['data_shift']
                           or -1),
            shared_table=('share_table' in attrs
                          and attrs['share_table'] == "True" or False),
            symmetry=('symmetry' in attrs and attrs['symmetry'] == "True"
                      or False),
            dense_steps=int('dense_steps' in attrs and attrs['dense_steps']
                            or 256),
            pointwise_shift=('pointwise_shift' in attrs
                             and attrs['pointwise_shift'] == "True" or False),
        )

        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)

        assert len(input_names) == 1
        assert len(output_names) == 1
        ishift_0 = _get_element(tname_shifts[input_names[0]], 1, 0)

        output_shift, aux_raw_data = lut.init(param, ishift_0)  # pylint: disable=unused-variable
        tname_shifts[output_names[0]] = [output_shift]
        # Note: If LUT output is int8, its actual shift is output_shift-8.
        # Since we use "tname_shifts" to determine valid range of
        # following tensors, we need to record its actual values here.
        if s.attr('out_type') == 'int8':
            tname_shifts[output_names[0]] = [output_shift - 8]

        assert len(aux_raw_data) == len(shift_names)

        aux_data[shift_names[0]] = mxnet.nd.array(
            aux_raw_data[0], dtype=np.int32)
        aux_data[shift_names[1]] = mxnet.nd.array(
            aux_raw_data[1], dtype=np.int32)

        for i in range(2, len(aux_raw_data)):
            val = aux_raw_data[i]
            assert int(val) == val
            aux_data[shift_names[i]] = mxnet.nd.array([int(val)],
                                                      dtype=np.int32)

        if options['debug'] > 1:
            print(output_names[0], '=', tname_shifts[output_names[0]],
                  " (absent in param file)")

    def rand_srelu(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)

        assert len(output_names) == 1
        if s.attr("activation_type") == "LeakyReLU":
            assert len(input_names) == 1
            assert len(shift_names) == 2  # scale, shift
            assert s.attr("slope"), "leaky relu need attr.slope"
            scale_float = float(s.attr("slope"))
            if scale_float == 1.0:
                scale_shift = 0
            else:
                scale_shift = int(math.log2(127.0 / abs(scale_float - 1.0)))
            scale_base = pow(2, scale_shift)
            scale_int32 = round(scale_float * scale_base)
            aux_data[shift_names[0]] = mxnet.nd.array([scale_int32],
                                                      dtype=np.int32)
            aux_data[shift_names[1]] = mxnet.nd.array([scale_shift],
                                                      dtype=np.int8)
        else:
            assert False, "srelu activation type " + s.attr(
                "activation_type") + " not implemented"

    def rand_color_converter(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        assert len(output_names) == 1
        assert len(input_names) == 3
        assert len(shift_names) == 1

        wname = input_names[1]
        bname = input_names[2]
        sname = shift_names[0]
        # rgb to yuv
        aux_data[sname] = mxnet.nd.array([8, 8, 8], dtype=np.int8)
        tname_data[wname] = mxnet.nd.array(
            [[59, 151, 29], [128, -107, -21], [-43, -85, 128]], dtype=np.int8)
        tname_data[bname] = mxnet.nd.array([0, 0, 0], dtype=np.int32)

    def pass_correlation(s):
        input_names, output_names, _ = _get_inputs_outputs_shifts(s)
        assert len(input_names) == 2
        assert len(output_names) == 1
        otname = _get_element(output_names, 1, 0)
        assert s.attr('output_shift') is not None, "missing attr.output_shift"
        tname_shifts[otname] = [int(s.attr('output_shift'))]

    def rand_quantishuffle(s):
        input_names, output_names, shift_names = _get_inputs_outputs_shifts(s)
        assert len(input_names) == 1
        assert len(output_names) == 1
        assert len(shift_names) == 1

        input_channel = options['all_shapes'][input_names[0]][-1]
        aux_data[shift_names[0]] = mxnet.nd.random.randint(
            0, input_channel, shape=(input_channel,), dtype=np.int32)
        ishift_0 = _get_element(tname_shifts[input_names[0]], 1, 0)
        tname_shifts[output_names[0]] = [ishift_0]

    # generate params, with the following handlers
    handlers = {
        'QuantiInput': rand_quantiinput,
        'SQuantiInput': rand_squantiinput,
        'AlphaPlusConvolution': rand_conv,
        'SAlphaPlusConvolution': rand_sconv,
        'QuantiDeconvolution': rand_conv,
        'AlphaPooling': pass_on_shift,
        'RoiAlign_X2': pass_on_first_input_shift,
        'AlphaFPNROIResize': pass_on_second_input_shift,
        'QuantiFlatten': pass_on_shift,
        'Concat': check_predefined_shift,
        'SliceChannel': check_predefined_shift,  # split
        'MulAdd': rand_elementwise,
        'broadcast_greater': rand_binary_no_shift,
        'broadcast_lesser': rand_binary_no_shift,
        'broadcast_greater_equal': rand_binary_no_shift,
        'broadcast_lesser_equal': rand_binary_no_shift,
        'broadcast_equal': rand_binary_no_shift,
        'broadcast_not_equal': rand_binary_no_shift,
        'SoftmaxOutput': rand_softmaxoutput,
        'ParsingPostProcessing_X2': pass_on_shift,
        'DetectionPostProcessing_X2': rand_dpp,
        'detection_thresh': pass_on_shift,
        'AlphaWarp': pass_on_for_warp,
        'QuantiChannelSum': rand_channelsum,
        'slice': pass_on_shift,
        'reorder_upscale': pass_on_shift,
        'channel_argmax': pass_on_shift,
        'LUT': handle_lut,
        'RCNNPostProcessing_X2': pass_on_shift,
        'AlphaResize': pass_on_shift,
        'AlphaSrelu': rand_srelu,
        'ColorConverter': rand_color_converter,
        'Pad': pass_on_shift,
        'QuantiCorrelation': pass_correlation,
        'QuantiShuffle': rand_quantishuffle,
    }

    options['input_index'] = 0
    for symbol in all_symbols_tuple:
        op = symbol.attr('op_type_name')
        if op == 'null':
            continue

        if op not in handlers:
            print('generating param for %s is not implemented' % op)
            inames, onames, snames = _get_inputs_outputs_shifts(symbol)
            print('inputs : %s' % ' '.join(inames))
            print('outputs: %s' % ' '.join(onames))
            print('shifts : %s' % ' '.join(snames))
            sys.exit(-1)

        handler = handlers[op]
        handler(symbol)

    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print(
            'elapsed_time=%.3f, after random_params, %d shifts, %d data, %d aux'
            % (float(elapsed_time), len(sname_shifts), len(tname_data),
               len(aux_data)))

    # convert to NDArray and check
    params = dict()
    for name in sname_shifts:
        temp = params['aux:' + name] = mxnet.nd.array(
            sname_shifts[name], dtype=np.int8)
        assert options['all_shapes'][name] == temp.shape

    for name in tname_data:
        temp = params['arg:' + name] = tname_data[name]
        assert options['all_shapes'][name] == temp.shape

    for name in aux_data:
        temp = params['aux:' + name] = aux_data[name]
        assert options['all_shapes'][name] == temp.shape

    # TODO: The current implementation requires partial param file
    # does not have any entry that affects shift inference
    if options['partial_param']:
        partial = mxnet.nd.load(options['partial_param'])
        for key, val in partial.items():
            params[key] = val

    if options['zero_param']:
        for val in params.values():
            val[:] = 0

    mxnet.nd.save(options['param'], params)
    # print('info: random params generated to', options['param'])
    return params


def check_samename(options):
    """
    Check if any nodes have the same name
    """
    with open(options['model'], 'r') as f:
        json_dicts = json.load(f)
        nodes = json_dicts['nodes']
        name_set = set()
        for i, node in enumerate(nodes):
            if node['name'] in name_set:
                print('duplicated node name "', node['name'], '", node index',
                      i)
                sys.exit(1)
            name_set.add(node['name'])


def run_predictor(options):
    """
    :param options: system arguments of this script
    :param input_npas: numpy arrays, float
    :return:
    """

    check_samename(options)

    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print('elapsed_time=%.3f, start predictor' % float(elapsed_time))

    with open(options['model'], 'r') as f:
        output_symbols = mxnet_predict.load_json(f.read())
    all_symbols = output_symbols.get_internals()
    mxnet_input_params = output_symbols.list_arguments(
    )  # The input of the param model

    # iterate on "all_symbols" is quite slow, so change to tuple first
    all_symbols_tuple = tuple(x for x in all_symbols)
    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print('elapsed_time=%.3f, after generating tuple of symbols' %
              float(elapsed_time))

    # infer shape, pass tuple to speedup
    infer_shape(options, all_symbols, all_symbols_tuple)
    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print(
            'elapsed_time=%.3f, after inferring shapes' % float(elapsed_time))

    # generate param, pass tuple to speedup
    if not options['gen_random_input_and_exit']:
        params = get_param(options, all_symbols_tuple)
    if options['gen_random_param_and_exit']:
        if predictor_cache and options["update_cache"]:
            predictor_cache.upload()
        sys.exit(0)
    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print('elapsed_time=%.3f, after generating input binaries' %
              float(elapsed_time))

    # get input names and shifts
    model_float_input_names = []
    model_input_shifts = []
    model_input_scales = []
    quant_by_scale = False
    model_integer_input_names = []
    model_input_types = []
    model_extra_input_names = []
    layers = []  # no duplicate
    layer_names = []  # tell pridictor which layers are output, may duplicate

    fixed_input_shape_map = {}

    for symbol in all_symbols_tuple:
        op = symbol.attr('op_type_name')

        if op != 'null':
            layers.append(symbol)
            layer_names.append(symbol.attr('name').encode(encoding="utf-8"))

        if op == 'QuantiInput' and symbol.list_arguments(
        )[0] in mxnet_input_params:
            symbols_of_qi = symbol.get_internals()
            # input float name
            assert len(symbols_of_qi.list_outputs(
            )) == 3, 'quantiinput should have 3 nodes: input, shift, output'
            model_float_input_names.append(symbols_of_qi[0].attr('name'))

            if not options['gen_random_input_and_exit']:
                # input shift
                if symbol.attr('fixed_output_shift') and \
                        int(symbol.attr('fixed_output_shift')) != -128:
                    shift_value = int(symbol.attr('fixed_output_shift'))
                    model_input_shifts.append(shift_value)
                else:
                    shift_value = params['aux:' + \
                                         symbols_of_qi[1].attr('name')]
                    model_input_shifts.append(shift_value.asnumpy().item(0))
            # output integer name
            model_integer_input_names.append(symbol.list_outputs()[0])
            if symbol.attr('out_type') == 'int16':
                model_input_types.append('int16')
            elif symbol.attr('out_type') == 'int32':
                model_input_types.append('int32')
            else:
                model_input_types.append('int8')

        if op == 'SQuantiInput' and symbol.list_arguments(
        )[0] in mxnet_input_params:
            quant_by_scale = True
            symbols_of_qi = symbol.get_internals()
            # input float name
            assert len(symbols_of_qi.list_outputs(
            )) == 3, 'quantiinput should have 3 nodes: input, shift, output'
            model_float_input_names.append(symbols_of_qi[0].attr('name'))

            if not options['gen_random_input_and_exit']:
                # input shift
                scale_value = params['aux:' + \
                                     symbols_of_qi[1].attr('name')]
                model_input_scales.append(scale_value.asnumpy().item(0))
            # output integer name
            model_integer_input_names.append(symbol.list_outputs()[0])
            model_input_types.append('int8')

        if op in ("RCNNPostProcessing_X2", "DetectionPostProcessing_X2") \
                and symbol.attr('image_size_fixed') == "False":
            symbols_of_qi = symbol.get_internals()
            symbol_arguments = symbols_of_qi.list_arguments()
            im_info_index = -1
            while symbol_arguments[im_info_index].find('weight') != -1 \
                    or symbol_arguments[im_info_index].find('bias') != -1:
                im_info_index -= 1
            im_info = symbol_arguments[im_info_index]
            if im_info in model_float_input_names:
                continue
            model_float_input_names.append(im_info)
            model_integer_input_names.append(im_info)
            fixed_input_shape_map[im_info] = (0, 2)  # 0 for batch N
            model_input_types.append('int32')
            if not options['gen_random_input_and_exit']:
                model_input_shifts.append(0)
                model_input_scales.append(1)

        name = symbol.attr('name')
        if (op == 'RoiAlign_X2' and symbol.attr('feature_map_resize_mode') !=
                'True') or op == 'AlphaFPNROIResize':
            roi_index = -1
            if op == 'AlphaFPNROIResize':
                roi_index = 0
            roi_tensor_name = symbol.get_children().list_outputs()[roi_index]
            # if roi_tensor_name in model_integer_input_names:
            #     continue
            roi_gen_symbol = None
            for s in all_symbols_tuple:
                if roi_tensor_name in s.list_outputs():
                    roi_gen_symbol = s
                    break
            assert roi_gen_symbol is not None, "can not find roi definer layer for roialign"
            if roi_gen_symbol.attr('op_type_name') == 'null':
                ## roi is input
                model_integer_input_names.append(roi_gen_symbol.attr('name'))
                model_float_input_names.append(roi_gen_symbol.attr('name'))
                model_input_types.append('int32')
                ## check/set roi input shape
                user_given_roi_shape = options['shape'][
                    len(model_float_input_names) - 1]
                roi_num = user_given_roi_shape[-2]
                if not roi_gen_symbol.attr('__shape__'):
                    pass
                else:
                    roi_num_in_model = eval(  # pylint: disable=eval-used
                        roi_gen_symbol.attr('__shape__'))[-2]
                    if 'roi_pad_n' not in options:
                        options['roi_pad_n'] = [roi_num_in_model - roi_num]
                    else:
                        options['roi_pad_n'].append(roi_num_in_model - roi_num)
                    if 'roi_index' not in options:
                        options['roi_index'] = [
                            len(model_float_input_names) - 1
                        ]
                    else:
                        options['roi_index'].append(
                            len(model_float_input_names) - 1)
                    if roi_num_in_model - roi_num != 0:
                        print(
                            "warning: roi number does not match with number in model, will pad invalid boxes or "
                            "remove redundant boxes.")

                if not options['gen_random_input_and_exit']:
                    model_input_shifts.append(0)
                    model_input_scales.append(1)
            elif roi_gen_symbol.attr('op_type_name') == 'QuantiInput':
                # roi is input from quanti input
                if 'roi_index' not in options:
                    options['roi_index'] = [len(model_float_input_names) - 1]
                else:
                    options['roi_index'].append(
                        len(model_float_input_names) - 1)
                if 'roi_pad_n' not in options:
                    options['roi_pad_n'] = [0]
                else:
                    options['roi_pad_n'].append(0)

    assert len(model_integer_input_names) + len(model_extra_input_names) \
           == len(options['shape']), \
        "The actual number of input %d does not equal" \
        " to number of inputs in options %d" \
        % (len(model_integer_input_names), len(options['shape']))

    # layer_names = list(set(layer_names))
    # assert len(set(layer_names)) == len(layer_names), 'duplicated layer name?'

    # get other names
    model_output_names = output_symbols.list_outputs()
    argument_names = set(output_symbols.list_arguments()) - set(
        model_float_input_names)  # weight, bias
    auxiliary_names = set(
        output_symbols.list_auxiliary_states())  # 'xxx_shift_history'
    all_names = [x for x in all_symbols.list_outputs()]
    feature_names = [
        x for x in all_names if x not in (argument_names | auxiliary_names)
    ]
    assert len(
        set(feature_names)) == len(feature_names), 'duplicated feature name?'

    # ugly hack: int32 may be int32 or int16, so we need to check symbol to
    # determine the real data type
    int16_feature_names = set()
    for symbol in all_symbols_tuple:
        symbol_name = symbol.attr('name')
        if symbol_name not in (argument_names |
                               auxiliary_names):  # an operator, not arg or aux
            allow_int16 = symbol.attr('op_type_name') in (
                'MulAdd', 'Lut', 'AlphaPlusConvolution',
                'SAlphaPlusConvolution', 'QuantiChannelSum', 'LUT',
                'AlphaPooling', 'QuantiInput', "SQuantiInput")
            if symbol.attr(
                    'out_type'
            ) == 'int16':  # should check MulAdd, SAlphaPlusConvolution
                assert allow_int16
                int16_feature_names |= set(symbol.list_outputs())

    if options['debug'] > 1:
        print('model inputs (float, shift, integer): ')
        pprint.pprint(
            list(
                zip(model_float_input_names, model_input_shifts,
                    model_integer_input_names)))
        print('model outputs: ', model_output_names)
        print('layers: ')
        pprint.pprint(layer_names)
        print('features: ')
        pprint.pprint(feature_names)
        print('int16 features: ', int16_feature_names)
        print('arguments: ')
        pprint.pprint(argument_names)
        print('auxiliaries: ')
        pprint.pprint(auxiliary_names)

    # prepare input info
    input_npas = get_input_numpy_arrays(
        options, model_float_input_names, model_extra_input_names,
        model_input_scales if quant_by_scale else model_input_shifts,
        model_input_types, quant_by_scale, output_symbols)

    if options['gen_random_input_and_exit']:
        if predictor_cache and options["update_cache"]:
            predictor_cache.upload()
        #    predictor_cache.upload()
        sys.exit(0)
    input_type_map = {}
    input_npa_map = {}
    input_shape_map = {}
    # get values of each layer
    tensors = OrderedDict()
    tensor_name_sym_map = {}
    if options['input_name'][0]:
        assert len(options['input_name']) == len(model_float_input_names)
        assert sorted(options['input_name']) == sorted(model_float_input_names)
        model_float_input_names = options['input_name']

    is_fpn_roiresize = False
    for symbol in output_symbols.get_internals():
        op = symbol.attr('op_type_name')
        if op == 'AlphaFPNROIResize':
            is_fpn_roiresize = True

    for i, input_name in enumerate(model_float_input_names):
        if 'roi_index' in options and i in options[
                'roi_index'] and not is_fpn_roiresize:
            input_type_map[input_name] = np.int32
        else:
            input_type_map[input_name] = np.float32
        input_npa_map[input_name] = input_npas[i]
        if input_name in fixed_input_shape_map:
            tmp_shape_list = list(fixed_input_shape_map[input_name])
            tmp_shape_list[0] = input_npas[i].shape[0]
            input_shape_map[input_name] = tuple(tmp_shape_list)
        else:
            input_shape_map[input_name] = input_npas[i].shape
        tensor = TensorData(input_name, input_npa_map[input_name],
                            TensorData.MODEL_INPUT)
        tensors[input_name] = tensor
    for i, input_name in enumerate(model_extra_input_names):
        input_type_map[input_name] = np.float32
        input_npa_map[input_name] = input_npas[len(model_float_input_names) +
                                               i]
        input_shape_map[input_name] = input_npas[len(model_float_input_names) +
                                                 i].shape
        tensor = TensorData(input_name, input_npa_map[input_name],
                            TensorData.MODEL_INPUT)
        tensors[input_name] = tensor

    param_tensors = mxnet.nd.load(options['param'])
    for input_name, t in param_tensors.items():
        if input_name[:4] == "aux:" or input_name[:4] == "arg:":
            # Remote MXNET specific param tensor name prefix
            input_name = input_name[4:]
        tensor = TensorData(input_name, t, TensorData.MODEL_PARAM)
        tensors[input_name] = tensor

    # infer type and run predictor, specifying layers to dump
    all_symbols.infer_type(**input_type_map)

    json_data = open(options['model'], 'r').read()

    json_data = update_json_data(json_data, options['march'])

    predictor = mxnet_predict.Predictor(
        json_data,
        open(options['param'], 'rb').read(),
        input_shape_map,
        num_output=len(layer_names),
        out_keys=layer_names,
        dev_type='cpu',
        input_types=input_type_map)

    predictor.forward(**input_npa_map)
    op_outputs = {
    }  # layer name to list of sym + ALL its outputs. One op could have multiple outputs

    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print('elapsed_time=%.3f, after predictor' % float(elapsed_time))

    for layer_index, layer in enumerate(layers):
        # get feature name and data
        output_feature_names = layer.list_outputs()
        layer_name = layer.name
        feature_name = _get_element(output_feature_names, 1, 0)
        feature_data = predictor.get_output(layer_index)
        # dump feature values to binary file
        feature_data_type = feature_data.dtype
        if feature_name in int16_feature_names:
            assert feature_data_type == np.dtype('int32'), feature_data_type
            feature_data_type = np.dtype('int16')
        assert len(feature_data.shape) <= 4
        while len(feature_data.shape) < 4:
            feature_data.shape = (1,) + feature_data.shape

        # Put the output batch dimension in the N channel rather than H
        # channel for easier dimension handling in HBDK3
        if layer.attr('op_type_name').find('DetectionPostProcess') != -1:
            assert feature_data.shape[0] == 1 or feature_data.shape[1] == 1
            feature_data.shape = (
                feature_data.shape[1] * feature_data.shape[0], 1,
                feature_data.shape[2], feature_data.shape[3])
        # Change Filter output shape so that as similar as possible with torch result
        if layer.attr('op_type_name').find('filter') != -1:
            feature_data.shape = (1, 1,
                                  feature_data.shape[0] * feature_data.shape[1]
                                  * feature_data.shape[2],
                                  feature_data.shape[3])

        if layer_name not in op_outputs:
            op_outputs[layer_name] = [layer]
        op_outputs[layer_name].append(feature_data)
        tensor = TensorData(
            feature_name, feature_data,
            (feature_name in model_output_names) and TensorData.MODEL_OUTPUT
            or TensorData.MODEL_INTERMEDIATE)
        tensors[feature_name] = tensor
        tensor_name_sym_map[feature_name] = layer

    for sym_and_outputs in op_outputs.values():
        sym = sym_and_outputs[0]
        outputs = sym_and_outputs[1:]
        converteds = convert_to_hardware_layout(sym, outputs, options['march'],
                                                sym.attr('op_type_name'),
                                                sym.list_attr())
        if not converteds:
            continue
        for i, data in enumerate(converteds):
            output_name = sym.name + "_output" + (
                str(i) if len(converteds) > 1 else "") + "_inhardwarelayout"
            tensor = TensorData(output_name, data,
                                TensorData.MODEL_INTERMEDIATE)
            tensors[output_name] = tensor
            tensor_name_sym_map[output_name] = sym

    # Output files are named by following rule:
    #
    # hbdk_output_${FEATURE_NAME}.txt
    #
    # Model verifier relies on the file names and headers to compare output tensors.
    # Please modify model verifier's code correspondingly if there is any modification!
    if options['gen_txt_output']:
        os.makedirs(os.path.abspath(options["output"]), exist_ok=True)
        output_tensor_names = output_symbols.list_outputs()
        for orig_output_tensor_name in output_tensor_names:
            output_tensor_name = re.split(r'\d+$', orig_output_tensor_name)[0]
            tmp_name1 = output_tensor_name + '_inhardwarelayout'
            tmp_name2 = orig_output_tensor_name + '_inhardwarelayout'
            hardwarelayout_output_tesnor_names = []
            for name in tensors:
                if name.find(tmp_name1) != -1:
                    hardwarelayout_output_tesnor_names.append(name)
                elif name.find(tmp_name2) != -1:
                    hardwarelayout_output_tesnor_names.append(name)
            if hardwarelayout_output_tesnor_names:
                for name in hardwarelayout_output_tesnor_names:
                    output_filename = os.path.join(
                        os.path.abspath(options["output"]),
                        'hbdk_output_' + name + '.txt')
                    tmp_dim = int(1)
                    data = tensors[name].data
                    for dim in data.shape:
                        tmp_dim *= dim
                    tmp_dim /= data.shape[-1]
                    tmp_dim = int(tmp_dim)
                    output_reshape = data.reshape((tmp_dim, data.shape[-1]))
                    np.savetxt(output_filename, output_reshape, fmt='%.20e')
            else:
                output_filename = os.path.join(
                    os.path.abspath(options["output"]),
                    'hbdk_output_' + orig_output_tensor_name + '.txt')
                tmp_dim = int(1)
                data = tensors[orig_output_tensor_name].data
                for dim in data.shape:
                    tmp_dim *= dim
                tmp_dim /= data.shape[-1]
                tmp_dim = int(tmp_dim)
                output_reshape = data.reshape((tmp_dim, data.shape[-1]))
                np.savetxt(output_filename, output_reshape, fmt='%.20e')
    else:
        os.makedirs(os.path.dirname(options["output"]), exist_ok=True)
        onnx_model = onnx_pb2.ModelProto()
        for name, t in tensors.items():
            assert name == t.name
            t.add_to_model_proto(onnx_model)
        onnx_model.producer_name = "mxnet-horizion"
        onnx_model.producer_version = mxnet.__horizon_version__
        mxnet_json = onnx_model.metadata_props.add()
        mxnet_json.key = "mxnet_json"
        mxnet_json.value = open(options['model'], "r").read()
        silent_remove_file(options["output"])
        with open(options["output"], "wb") as f:
            serialized = onnx_model.SerializeToString()
            if not serialized:
                print('warning: cannot generate reference data')
            f.write(serialized)

    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print(
            'elapsed_time=%.3f, after writing pred.onnx' % float(elapsed_time))


def update_json_data(json_data, march):
    """
    Update MXNET json data.
    For example, give default value for dpp
    """
    json_dict = json.loads(json_data)
    enable_tile = march not in [
        hbdk.config.March.BAYES.name, hbdk.config.March.B25E.name,
        hbdk.config.March.B253.name
    ]
    for node in json_dict['nodes']:
        if node['op'] == 'DetectionPostProcessing_X2':
            attr = node['attr']
            changed = False
            if enable_tile:
                if '__h_block_size_list__' not in attr or \
                        attr['__h_block_size_list__'].find("-") != -1:
                    attr['__h_block_size_list__'] = str([64, 64, 64, 64, 64])
                    changed = True
                if '__w_block_size_list__' not in attr or \
                        attr['__w_block_size_list__'].find("-") != -1:
                    attr['__w_block_size_list__'] = str([64, 64, 64, 64, 64])
                    changed = True
            else:
                if '__h_block_size_list__' not in attr or \
                        attr['__h_block_size_list__'].find("-") != -1:
                    attr['__h_block_size_list__'] = str([-1, -1, -1, -1, -1])
                    changed = True
                if '__w_block_size_list__' not in attr or \
                        attr['__w_block_size_list__'].find("-") != -1:
                    attr['__w_block_size_list__'] = str([-1, -1, -1, -1, -1])
                    changed = True
            if changed:
                if enable_tile:
                    print("NOTE: DetectionPostProcessing_X2"
                          " block size is set to 64")
                else:
                    print("NOTE: DetectionPostProcessing_X2"
                          " block size is set to -1")
        elif node['op'] == 'RoiAlign_X2' and \
                (march in [hbdk.config.March.BAYES.name, hbdk.config.March.B25E.name, hbdk.config.March.B253.name]):
            attr = node['attr']
            is_upscale_mode = None
            if 'feature_map_resize_mode' in attr:
                is_upscale_mode = attr['feature_map_resize_mode']
            if is_upscale_mode == 'False' or is_upscale_mode == '0' or is_upscale_mode is None:
                changed = False
                if 'bilinear_line_quantization' not in attr or \
                        attr['bilinear_line_quantization'] == '1':
                    attr['bilinear_line_quantization'] = '0'
                    changed = True
                if changed:
                    print(
                        "NOTE: RoiAlign_X2 bilinear_line_quantization is disabled on current march"
                    )
        if node['op'] != "null":
            if 'attr' not in node:
                node['attr'] = {}
            attr = node['attr']
            if '__predict__' not in attr:
                attr['__predict__'] = 'True'
    return json.dumps(json_dict, indent=2, sort_keys=True)


def main():
    register_exit_gracefully_handler()
    start = time.time()

    options = parse_args()

    if options['debug'] > 0:
        options['start_time'] = start

    globals()['predictor_cache'] = None
    if options['cache_server'] and options[
            'cache_root'] and options['framework'] != 'hbir':
        register_exit_gracefully_handler()
        from hbdk.test.predictor_cache import PredictorCache
        globals()['predictor_cache'] = PredictorCache(options)
        result = predictor_cache.try_load_cache()
        if result:
            sys.exit(0)
        else:
            print("Predictor cache not loaded. Remove output files")
            predictor_cache.remove_output_files()

    import_modules()
    if options['framework'] == 'tensorflow':
        from . import pred_tf
        pred_tf.main(options)
        sys.exit(0)
    elif options['framework'] == 'hbir':
        from . import pred_hbir
        pred_hbir.main(options)
        sys.exit(0)
    elif options['framework'] == 'torch':
        from hbdk.tools import pred_torch
        pred_torch.main(options)
        sys.exit(0)

    # run predictor and dump features to binary files
    run_predictor(options)

    if predictor_cache and options["update_cache"]:
        predictor_cache.upload()
    elapsed_time = time.time() - start
    if options['time'] is not None:
        # There numbers: real time, user time, system time.
        # Haven't found the way to record user time and system time in Python though
        # NOTE: DO NOT remove user time or system time, otherwise the format is not consistent with C++ programs.
        if not options['time']:  # Empty string
            print(
                '# hbdk-pred %.3f %.3f 0' % (float(elapsed_time),
                                             float(elapsed_time)),
                file=sys.stderr)
        else:
            msg = "# %.3f %.3f 0 hbdk-pred" % (float(elapsed_time),
                                               float(elapsed_time))
            for i in range(1, len(sys.argv)):
                msg += " " + sys.argv[i]
            with open(options['time'], "a") as f:
                print(msg, file=f)

    if options['debug'] > 0:
        elapsed_time = time.time() - options['start_time']
        print('elapsed_time=%.3f, done' % float(elapsed_time))


if __name__ == "__main__":
    main()
