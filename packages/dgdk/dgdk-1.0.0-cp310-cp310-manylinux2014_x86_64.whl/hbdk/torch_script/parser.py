import torch
import numpy as np
import re

from hbdk.config import March, get_normalized_march

from hbdk.torch_script.utils import hbir_base
from hbdk.torch_script.utils import check_const_prop, aten_const_prop, unwrap_attr_get, TensorManager, assign_pred
from hbdk.torch_script.placeholder import placeholder
import hbdk.torch_script.prim_registry as prim
import hbdk.torch_script.aten_registry as aten

from typing import List


class ScopeManager(object):
    # manage scope name and symbols
    def __init__(self, name):
        self._scopes = []
        self._scope_name = []
        self.enter_scope(name)

    def enter_scope(self, suf: List[str]):
        # enter a new scope, append a new dict
        self._scope_name.append(".".join(suf))
        self._scopes.append({})
        self._cur_scope = self._scopes[-1]

    def exit_scope(self):
        self._scopes.pop()
        self._cur_scope = self._scopes[-1]
        self._scope_name.pop()

    def lookup(self, k):
        return self._cur_scope[k]

    def lookup_name(self, n, level=-1):
        for k in self._scopes[level].keys():
            if k.debugName() == n:
                return self._scopes[level][k]
        return

    def key_names(self):
        return [k.debugName() for k in self._cur_scope.keys()]

    def insert(self, k, v):
        self._cur_scope[k] = v

    def scope_name(self, delimiter="."):
        return delimiter.join(self._scope_name)


class HBIRBuilder(object):
    def __init__(self, func_name, march, run_pred=False):

        self.scope_man = ScopeManager([func_name])
        self.jit_module = None
        self.func_name = func_name
        self.march_enum = get_normalized_march(march)
        self.run_pred = run_pred
        self.pred_record = dict()
        self.inhardware_pred_record = dict()

        self.args = []
        self.arg_names = []

        self.rets = []
        self.ret_names = []

        self.annotations = []

        self.pt_input_names = []
        self.pt_output_names = []

    def _visit_node(self, node):
        assert isinstance(node, torch._C.Node)
        namespace, op = node.kind().split("::")

        if namespace == 'aten' and op.endswith('_') and not op.endswith(
                '__'):  # normalize aten inplace version
            op = op[:-1]

        func_name = namespace + '_' + op
        raw_args = [self.scope_man.lookup(i) for i in node.inputs()]

        if namespace == 'prim':
            if hasattr(prim, func_name):
                try:
                    getattr(prim, func_name)(self, node, *raw_args)
                    return
                except:
                    raise ValueError(
                        "parsing prim node", node, "in named childern",
                        self.scope(), "args are", raw_args)
            else:
                raise ValueError('unsupported node', node, 'in named children',
                                 self.scope())

        # unwrap attr get
        args = unwrap_attr_get(raw_args)
        if check_const_prop(args):
            try:
                ret = aten_const_prop(self, node, namespace, op, *args)
            except:
                raise ValueError("constant propagation aten node", node,
                                 "failed. Report to HBDK Group.")

        # lookup aten registry
        elif hasattr(aten, func_name):
            annotated_name = self.get_annotation(func_name)
            try:
                ret = getattr(aten, func_name)(self, annotated_name, node,
                                               *args)
            except:
                raise ValueError("parsing aten node", node,
                                 "in named childern", self.scope(), "args are",
                                 raw_args)
            if self.run_pred:
                aten.run_pred(self, ret, namespace, op, args)
        else:
            raise ValueError('unsupported node', node, 'in named children',
                             self.scope())

        # assign return
        if node.outputsSize() != 1:
            for i in range(node.outputsSize()):
                self.scope_man.insert(node.outputsAt(i), ret[i])
        else:
            self.scope_man.insert(node.outputsAt(0), ret)

    def scope(self, delimiter="."):
        return self.scope_man.scope_name(delimiter)

    def save_pred_record(self, file):
        """Convert prediction result into to onnx tensor buffer"""

        from hbdk.proto import onnx_pb2
        from hbdk.tools.pred import TensorData

        onnx_model = onnx_pb2.ModelProto()

        names = [name for name in self.pred_record.keys()] + [
            name + '_inhardwarelayout' for name in self.pred_record.keys()
        ]
        for name in names:
            if name in self.inhardware_pred_record.keys():
                dtype, data = self.inhardware_pred_record[name]
            elif name in self.pred_record:
                dtype, data = self.pred_record[name]
            else:
                continue

            if data == None:
                continue
            if data.dtype != torch.float:  # maybe already dequantized
                if dtype == 'int4':  # no such data type
                    dtype = 'int8'
                if data.dtype == torch.bool:
                    assert dtype == 'int8'
                data = data.numpy().astype(
                    np.dtype(dtype))  # plugin int16 actually stored in int32
            else:
                data = data.numpy()
            if data is not None:
                tensor_type = TensorData.MODEL_INTERMEDIATE
                if name in self.arg_names:
                    tensor_type = TensorData.MODEL_INPUT
                if name in self.ret_names:
                    tensor_type = TensorData.MODEL_OUTPUT
                tensor_data = TensorData(name, data, tensor_type)
                tensor_data.add_to_model_proto(onnx_model)
        with open(file, "wb") as f:
            serialized = onnx_model.SerializeToString()
            if not serialized:
                print('warning: cannot generate reference data')
            f.write(serialized)

    def save_input(self, path):
        for name in self.arg_names:
            dtype, data = self.pred_record[name]
            data = data.numpy().astype(
                np.dtype(dtype))  # plugin int16 actually stored in int32
            data.tofile("%s/%s.bin" % (path, name))

    def get_annotation(self, call):
        anno = self.scope(".") + "." + call
        anno = anno.replace(".", "_")
        if anno not in self.annotations:
            self.annotations.append(anno)
            return anno

        start_idx = 1
        cur_anno = anno + "_" + str(start_idx)
        while cur_anno in self.annotations:
            start_idx += 1
            cur_anno = anno + "_" + str(start_idx)

        self.annotations.append(cur_anno)
        return cur_anno

    def _build_from_jit_script(self, jit, example_inputs):
        def arg_dfs(x, name):
            if isinstance(x, (list, tuple)):
                return [
                    arg_dfs(i, name + '[' + str(idx) + ']')
                    for idx, i in enumerate(x)
                ]
            if isinstance(x, dict):
                return {
                    k: arg_dfs(x[k], name + '[' + k + ']')
                    for k in sorted(x.keys())
                }
            if isinstance(x, placeholder):
                if self.run_pred and x.sample == None:
                    if x.dtype in [torch.float32]:
                        x.sample = torch.randn(x.shape, dtype=x.dtype)
                    elif x.dtype == torch.int8:
                        x.sample = torch.randint(
                            low=-128, high=127, size=x.shape, dtype=x.dtype)
                    elif x.dtype == torch.int16:
                        x.sample = torch.randint(
                            low=-32768,
                            high=32767,
                            size=x.shape,
                            dtype=x.dtype)
                    elif x.dtype == torch.int32:
                        x.sample = torch.randint(
                            low=-50000,
                            high=50000,
                            size=x.shape,
                            dtype=x.dtype)
                    else:
                        raise ValueError("unknown dtype to generate sample",
                                         x.dtype)
                tm = x.tensor_manager(name)
                self.args.append(tm)
                if self.run_pred:
                    assign_pred(self, tm, None)
                return tm
            return x

        def format_input(inputs):
            ret = []
            for idx, input in enumerate(inputs):
                ret.append(arg_dfs(input, "arg%d" % (idx)))
            return ret

        example_inputs = format_input(example_inputs)

        # append self to args
        if isinstance(jit, torch.jit.ScriptModule):
            actual_inputs = (jit, *example_inputs)
        elif isinstance(jit, torch.jit.ScriptFunction):
            actual_inputs = example_inputs
        else:
            raise ValueError("unknown torch.jit object", type(jit))

        # insert argument into current scope
        for k, v in zip(jit.graph.inputs(), actual_inputs):
            self.scope_man.insert(k, v)
        # loop through all nodes
        for node in jit.graph.nodes():
            self._visit_node(node)

        self.rets = self._flatten(
            [self.scope_man.lookup(o) for o in jit.graph.outputs()])
        if len(self.rets) == 0:
            raise ValueError("no output tensor found. empty model!")

    def _flatten(self, x):
        ret = []
        if isinstance(x, (list, tuple)):
            for i in x:
                ret.extend(self._flatten(i))
        elif isinstance(x, dict):
            for k in sorted(x.keys()):
                ret.extend(self._flatten(x[k]))
        elif isinstance(x, TensorManager):
            ret = [x]
        return ret

    def build_from_jit(self, jit_obj: torch.jit.ScriptModule
                       or torch.jit.ScriptFunction, example_inputs):
        hbir_base.CleanUpContext()
        if self.march_enum == March.BERNOULLI:
            hbir_base.SetSQuantiScope(False)
        else:
            hbir_base.SetSQuantiScope(True)

        if isinstance(example_inputs, (torch.Tensor, placeholder, dict)):
            example_inputs = [example_inputs]
        if isinstance(jit_obj, torch.jit.TracedModule):
            jit_obj = jit_obj._actual_script_module
        self._build_from_jit_script(jit_obj, example_inputs)
        # perform dfs & dce.
        self.hbir_model = hbir_base.Model(
            [r.retrieve().hbir for r in self.rets])

        self.arg_names = list(self.hbir_model.input_tensor_names)

        # default arguments are in an order of their first use.
        # Arrange the string order by the numbers within the string
        def split_string(string):
            """Split string into characters and numbers"""
            s_split = list(sum(re.findall(r'(\D+)(\d+)', 'a%s0' % string), ()))

            # Remove the manually added first character "a" and last character "0",
            # these characters are to make the string conform to the regular rule
            if s_split[0] == "a":
                del s_split[0]
            else:
                s_split[0] = s_split[0][1:]
            if s_split[-1] == "0":
                del s_split[-1]
            else:
                s_split[-1] = s_split[-1][:-1]

            s_convert = [int(s) if s.isdigit() else s for s in s_split]
            return s_convert

        # align arguments by sorting their names.
        self.arg_names.sort(key=split_string)
        self.ret_names = list(self.hbir_model.output_tensor_names)

        def get_pt_input_or_output(mode):
            jit_obj_graph_inouts = jit_obj.graph.inputs() if mode == "input" \
                else jit_obj.graph.outputs()
            tm_list = self._flatten(
                [self.scope_man.lookup(o) for o in jit_obj_graph_inouts])
            pt_tensor_names_tmp = list(record.hbir
                                       for tensor_manager in tm_list
                                       for record in tensor_manager.records)
            hbir_tensor_names_tmp = list(
                self.hbir_model.input_tensor_names if mode ==
                "input" else self.hbir_model.GetModelOutputTensorNames())
            pt_tensor_names = list(set(pt_tensor_names_tmp))
            pt_tensor_names.sort(key=pt_tensor_names_tmp.index)
            hbir_tensor_names = set(hbir_tensor_names_tmp)
            tensor_names = []
            for tensor_name in pt_tensor_names:
                if tensor_name in hbir_tensor_names:
                    tensor_names.append(tensor_name)
                else:
                    print("WARNING: When converting pt to hbir, model " +
                          mode + " " + '"' + tensor_name + '"' +
                          " was deleted!")
            return tensor_names

        self.pt_input_names = get_pt_input_or_output("input")
        self.pt_output_names = get_pt_input_or_output("output")

        self.hbir_model.AddInputOutputOrderLayer("input_output_order_layer",
                                                 self.pt_input_names,
                                                 self.pt_output_names)
