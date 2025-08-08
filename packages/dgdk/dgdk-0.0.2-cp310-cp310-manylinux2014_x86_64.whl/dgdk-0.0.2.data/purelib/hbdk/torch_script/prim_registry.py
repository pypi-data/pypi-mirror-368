import torch
import horizon_plugin_pytorch.nn.functional as hf
import horizon_plugin_pytorch.nn.quantized.functional as hqf
from hbdk.torch_script.utils import deduce_prim_Constant, AttrGet, check_const_prop, unwrap_attr_get, need_pred
import hbdk.torch_script.horizon_registry as horizon


def prim_Constant(builder, node):
    builder.scope_man.insert(node.outputsAt(0), deduce_prim_Constant(node))


def prim_GetAttr(builder, node, obj):  # obj unused
    attr = AttrGet(
        builder.scope_man.lookup(node.inputsAt(0)), deduce_prim_Constant(node))
    builder.scope_man.insert(node.outputsAt(0), attr)


def prim_CallFunction(builder, node, func, *args):
    raw_args = args
    # unwrap attr get
    args = unwrap_attr_get(raw_args)
    if check_const_prop(args):
        if hasattr(hqf, func):
            ret = getattr(hqf, func)(*args)
            builder.scope_man.insert(node.outputsAt(0), ret)
            return
        if hasattr(hf, func):
            ret = getattr(hf, func)(*args)
            builder.scope_man.insert(node.outputsAt(0), ret)
            return
        raise ValueError("unknown constant propagation on horizon function",
                         func, "in named childern", builder.scope(),
                         "args are", raw_args)

    # lookup horizon registry
    if hasattr(horizon, func):
        try:
            ret = getattr(horizon, func)(builder,
                                         builder.get_annotation('hz_' + func),
                                         node, *args)
        except:
            raise ValueError(
                "parsing horizon function", func, "in named childern",
                builder.scope(), "args are", raw_args)

        if builder.run_pred:  # run predictor
            horizon.run_pred(builder, ret, func, args)

        # assign return
        if node.outputsSize() != 1:
            for i in range(node.outputsSize()):
                builder.scope_man.insert(node.outputsAt(i), ret[i])
        else:
            builder.scope_man.insert(node.outputsAt(0), ret)
        return

    raise ValueError(
        "unsupported horizon jit function", func, "in named childern",
        builder.scope(), "args are", raw_args)


def prim_CallMethod(builder, parent_node, sub_module, *args):
    # enter a new scope
    sub_module_name = sub_module.name
    sub_module = sub_module()

    if isinstance(sub_module, torch.jit.TracedModule):
        sub_module = sub_module._actual_script_module

    method = getattr(sub_module, parent_node.s('name'))
    graph = method.graph

    if check_const_prop(args):  # support module const prop
        retv = [method(*unwrap_attr_get(args))]
    else:
        builder.scope_man.enter_scope(sub_module_name)
        argv = [sub_module, *args]
        argk = [i for i in graph.inputs()]

        for k, v in zip(argk, argv):
            builder.scope_man.insert(k, v)

        for node in graph.nodes():
            builder._visit_node(node)

        ret_node = graph.return_node()
        retv = [builder.scope_man.lookup(o) for o in ret_node.inputs()]

        builder.scope_man.exit_scope()

    for i, r in enumerate(retv):
        if isinstance(r, (tuple, list)):
            # type may mismatch due to shared module
            if parent_node.outputsAt(i).type().kind() == 'TupleType':
                builder.scope_man.insert(parent_node.outputsAt(i), r)
            elif parent_node.outputsAt(i).type().kind() == 'TensorType':
                builder.scope_man.insert(parent_node.outputsAt(i), r[0])
            else:
                assert parent_node.outputsAt(i).type().kind() == 'NoneType'
        else:
            builder.scope_man.insert(parent_node.outputsAt(i), r)


def prim_ListConstruct(builder, node, *args):
    builder.scope_man.insert(node.outputsAt(0), list(args))


def prim_TupleConstruct(builder, node, *args):
    builder.scope_man.insert(node.outputsAt(0), args)


def prim_ListUnpack(builder, node, list_to_unpack):
    assert isinstance(list_to_unpack, (list, tuple))
    for i, r in enumerate(list_to_unpack):
        builder.scope_man.insert(node.outputsAt(i), r)


def prim_TupleUnpack(builder, node, tuple_to_unpack):
    assert isinstance(tuple_to_unpack, (list, tuple))
    for i, r in enumerate(tuple_to_unpack):
        builder.scope_man.insert(node.outputsAt(i), r)


def prim_NumToTensor(builder, node, num):
    builder.scope_man.insert(node.outputsAt(0), torch.as_tensor(num))
