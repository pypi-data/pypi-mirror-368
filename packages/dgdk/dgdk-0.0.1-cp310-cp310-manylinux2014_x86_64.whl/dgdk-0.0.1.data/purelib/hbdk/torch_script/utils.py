from typing import List

import sys
if sys.version_info >= (3, 10):
    from collections.abc import Iterable
else:
    from collections import Iterable

import torch
import numpy as np
from hbdk.config import March
from hbdk import hbir_base


def perm_to_native(rank):
    spatial_dims = [i for i in range(1, rank - 1)]
    return [0, rank - 1, *spatial_dims]


def perm_from_native(rank):
    if rank == 1:
        return [0]
    spatial_dims = [i for i in range(2, rank)]
    return [0, *spatial_dims, 1]


class TensorRecord(object):
    """
    a helper class to manage hbir.Tensor
    """

    def __init__(self, hbir: str, torch_native: bool):
        self.torch_native = torch_native
        self.hbir = hbir

        if self.torch_native:
            assert '_torch_native' in self.hbir  # must include it.

        if self.torch_native:
            self.table = [i for i in range(self.rank())]
        else:
            self.table = perm_to_native(self.rank())

        if self.rank() <= 2:
            assert self.torch_native, "%d-d tensor %s must be torch_native".format(
                self.rank(), self.hbir)

    def dtype(self, dtype=None):
        if dtype != None:
            hbir_base.SetTensorDtype(self.hbir, dtype)
            return
        return hbir_base.GetTensorDtype(self.hbir)

    def shape(self, shape=None):
        if shape != None:
            hbir_base.SetTensorShape(self.hbir, shape)
            return
        return list(hbir_base.GetTensorShape(self.hbir))

    def rank(self):
        return len(list(hbir_base.GetTensorShape(self.hbir)))

    def scale(self, scale=None):
        if scale != None:
            hbir_base.SetTensorScale(self.hbir, torch_tensor_to_list(scale))
            return
        return list(hbir_base.GetTensorScale(self.hbir))

    def shift(self, scale=None):
        if scale != None:
            if scale.dtype == torch.float:
                scale = torch_tensor_to_list(scale)
                shift = []
                for s in scale:
                    m, e = np.frexp(s)
                    if m != 0.5:
                        raise ValueError('invalid scale is not power of 2')
                    shift.append(int(-e + 1))
            else:
                scale = torch_tensor_to_list(scale)
                shift = scale
            hbir_base.SetTensorShift(self.hbir, shift)
            return
        return list(hbir_base.GetTensorShift(self.hbir))

    def __repr__(self):
        return "TensorRecord(hbir=%s, size=%s, dtype=%s, scale=%s, shift=%s, torch_native=%s)" % (
            self.hbir, "x".join(str(x) for x in self.shape()), self.dtype(),
            str(self.scale()), str(self.shift()), str(self.torch_native))

    def process_name(self, name):
        if self.torch_native:
            if "_torch_native" not in name:
                return name + "_torch_native"
        return name

    def transpose_dim(self, dim):
        """
        A helper function to transpose dim attribute. e.g. dim of reduce_mean.
        :return: transposed dim
        """
        if isinstance(dim, Iterable):
            dim = [self.rank() + d if d < 0 else d for d in dim]
        if isinstance(dim, Iterable):
            dim = [self.table[d] for d in dim]
            dim.sort()
            return dim
        return self.table[dim]

    @staticmethod
    def transpose(record):
        """
        transpose a record between torch_native and non-torch_native.
        """
        rank = record.rank()
        if rank <= 2:
            raise ValueError(record.__repr__() + " should not reach here")

        name = record.hbir
        if record.torch_native:  # to non native
            assert '_torch_native' in record.hbir

            def remove_token(name, token):
                return name[:name.find(token)] + name[name.find(token) +
                                                      len(token):]

            name = remove_token(name, '_torch_native')
            perm = perm_from_native(record.rank())
        else:
            assert '_torch_native' not in record.hbir
            name += '_torch_native'
            perm = perm_to_native(record.rank())

        hbir = hbir_base.CreateTransposeLayer(record.hbir, name, perm, name)

        return TensorRecord(hbir, not record.torch_native)


class TensorManager(object):
    """
    a helper class to manage multiple instances of hbir.Tensor in order to avoid generating redundant hbir.transpose
    """

    def __init__(self, hbir: str, torch_native: bool, native_sample=None):
        self.records = [TensorRecord(hbir, torch_native)]
        self.native_sample = native_sample

    def __repr__(self):
        ret = 'TensorManager: '
        for idx, r in enumerate(self.records):
            ret += 'record[' + str(idx) + ']: ' + r.__repr__()
        return ret

    def dtype(self, dtype):
        assert len(self.records) != 0
        for tr in self.records:
            tr.dtype(dtype)

    def scale(self, scale):
        assert len(self.records) != 0
        for tr in self.records:
            tr.scale(scale)

    def shift(self, scale):
        assert len(self.records) != 0
        for tr in self.records:
            tr.shift(scale)

    def retrieve(self, torch_native=None):
        """
        return the specified version of hbir tensor, if not create one via hbir.transpose.
        :param torch_native: in 4dim tensor, corresponds to nhwc and nchw layout tensor
        :return: hbir.tensor
        """
        # 'torch_native' is specified, return it
        if torch_native is not None:
            assert len(self.records) != 0
            for tr in self.records:
                if torch_native == tr.torch_native:
                    return tr

            # no target one
            assert len(self.records) == 1
            tr = TensorRecord.transpose(self.records[0])
            self.records.append(tr)
            return tr

        # 'torch_native' not specified, return one, torch_native version is preferred
        for tr in self.records:
            if tr.torch_native:
                return tr
        return self.records[0]


def gen_rescale_param(iscale, itype, oscale, otype, march_enum):
    assert itype in ["int32", "int16", "int8", "int4"]
    assert otype in ["int32", "int16", "int8", "int4"]
    precision_bits = {"int32": 31, "int16": 15, "int8": 7, "int4": 3}
    if isinstance(iscale, torch.Tensor):
        iscale = iscale.cpu().contiguous().detach().numpy()
    if isinstance(oscale, torch.Tensor):
        oscale = oscale.cpu().contiguous().detach().numpy()

    bpu_oscale = iscale / oscale
    bpu_oscale = np.clip(bpu_oscale,
                         np.iinfo(np.int16).min,
                         np.iinfo(np.int16).max)

    if itype is "int32":
        if otype is "int32":
            return []

        # https://horizonrobotics.feishu.cn/wiki/wikcnXkIyTkfZ4z1s6ZW43rQCCh
        # clip 15 - e in range [0, 31], so e in range[-16, 15], only for int32 quantize

        m, e = np.frexp(bpu_oscale)
        qscale = np.clip(np.floor(m * (1 << 15) + 0.5), -32768, 32767)
        rshift = 15 - e
        max_post_rshift = 30 - 1 - precision_bits[otype]
        if march_enum in (March.BAYES, March.B25E):
            pre_rshift = np.clip(rshift - max_post_rshift, 0, 17)
        else:
            pre_rshift = np.clip(rshift - max_post_rshift, 0, 31)
        post_rshift = np.clip(rshift - pre_rshift, 0, 31)
        return qscale.astype(np.int32), post_rshift.astype(
            np.int32), pre_rshift.astype(np.int32)
    else:
        m, e = np.frexp(bpu_oscale)
        qscale = np.clip(np.floor(m * (1 << 15) + 0.5), -32768, 32767)
        rshift = np.clip(15 - e, 0, 31)
        return qscale.astype(np.int32), rshift.astype(
            np.int32), np.zeros(1).astype(np.int32)


def get_common_torch_native(x: List[TensorManager]):
    """
    return the most common torch_native state
    """
    torch_native = 0
    non_torch_native = 0
    for i in x:
        if isinstance(i, TensorManager):
            for r in i.records:
                if r.torch_native:
                    torch_native += 1
                else:
                    non_torch_native += 1
    torch_native = torch_native > non_torch_native  # non torch native is preferred

    for i in x:
        if isinstance(i, TensorManager):
            i.retrieve(torch_native)
    return torch_native


def to_hbir_tensor(inputs, annotated_name, dtypes, torch_native):
    """
    transform torch.Tensor to Tensor manager.
    """
    common_rank = 0
    for input in inputs:
        if isinstance(input, torch.Tensor):
            this_rank = len(input.size())
        elif isinstance(input, TensorManager):
            this_rank = input.retrieve().rank()
        else:
            raise ValueError("unknown tensor type", type(input))
        if common_rank < this_rank:
            common_rank = this_rank

    ret = []
    for idx, input, dtype in zip(range(len(inputs)), inputs, dtypes):
        if isinstance(input, torch.Tensor):
            assert 'int' in dtype, "only supports qint"
            postfix = "_const" + str(idx)
            # align constant rank to placeholder
            rank_diff = common_rank - len(input.size())
            if rank_diff > 0:
                shape = [1] * rank_diff
                shape.extend(input.size())
                input = input.view(shape)
            # permute to channel last if placeholder torch_native is True
            if torch_native:
                postfix += "_torch_native"
            else:
                input = torch.permute(input, perm_from_native(
                    len(input.size())))
            if dtype[0] == 'q':
                dtype = dtype[1:]
            hbir = hbir_base.CreateTensor(annotated_name + postfix,
                                          list(input.size()), dtype,
                                          torch_tensor_to_list(input), [], [])
            ret.append(TensorManager(hbir, torch_native))
        else:
            ret.append(input)
    return ret


def assign_pred(builder, ret, ret_sample):
    """
    assign pred result to tensor manager. skip if sample of tensor manager already set,
    """
    if isinstance(ret, (list, tuple)):
        if ret_sample == None:
            ret_sample = [None] * len(ret)
        for r, s in zip(ret, ret_sample):
            assign_pred(builder, r, s)
    elif isinstance(ret, TensorManager):
        if ret.native_sample == None:
            ret.native_sample = ret_sample
        for tr in ret.records:
            if tr.torch_native:
                if ret.native_sample.dtype == torch.float32:
                    builder.pred_record[tr.hbir] = [
                        'float32', ret.native_sample
                    ]
                else:
                    builder.pred_record[tr.hbir] = [
                        tr.dtype(), ret.native_sample
                    ]
            else:
                builder.pred_record[tr.hbir] = [
                    tr.dtype(),
                    torch.permute(ret.native_sample,
                                  perm_from_native(tr.rank()))
                ]


def unwrap_attr_get(args):
    """
    unwrap AttrGet in the arguments. AttrGet is designed to trace source of torch.Tensor.
    """
    ret = []
    for i in args:
        if isinstance(i, AttrGet):
            ret.append(i.__call__())
        elif isinstance(i, (list, tuple)):
            ret.append(unwrap_attr_get(i))
        else:
            ret.append(i)
    return ret


def unwrap_tensor_manager(args):
    """
    unwrap tensor manager and get the sample. This function only used by pred.
    """
    ret = []
    for i in args:
        if isinstance(i, TensorManager):
            ret.append(i.native_sample)
        elif isinstance(i, (list, tuple)):
            ret.append(unwrap_tensor_manager(i))
        else:
            ret.append(i)
    return ret


def need_pred(ret):
    """
    check if the return of the node already have sample set. if not, run pred.
    """
    if isinstance(ret, (list, tuple)):
        for r in ret:
            if need_pred(r):
                return True

    if isinstance(ret, TensorManager):
        return ret.native_sample == None
    return False


class AttrGet(object):
    """
    this object is designed to trace the source of a torch.Tensor.
    """

    def __init__(self, obj, name):
        if isinstance(obj, AttrGet):
            self.obj = obj.obj
            self.name = [*obj.name, name]
            pass
        elif isinstance(obj, torch.jit.ScriptModule):
            self.obj = obj
            self.name = [name]
        else:
            raise ValueError('invalid obj type', type(obj))

    def __call__(self):
        ret = self.obj
        for n in self.name:
            ret = getattr(ret, n)
        return ret

    def __repr__(self):
        return "object<" + ".".join(self.name) + ">"


def deduce_prim_Constant(node: torch._C.Node):
    """
    get constant value from prim::Constant node.
    """
    if len(node.attributeNames()) == 0:
        return None
    assert len(node.attributeNames()) == 1
    name = node.attributeNames()[0]
    kind = node.kindOf(name)

    if kind == "ival":  # tensor type
        return node.output().toIValue()
    if kind == 'i':
        return node.output().toIValue()
    return getattr(node,
                   kind)(name)  # scalar type, basically string, int, float...


def check_const_prop(args):
    """
    check if the node is constant propagation.
    """
    if isinstance(args, (dict, list, tuple)):
        for arg in args:
            if check_const_prop(arg):
                continue
            return False
    if isinstance(args, TensorManager):
        return False
    return True


def torch_tensor_to_list(t: torch.Tensor):
    if t == []:
        return t
    return t.cpu().contiguous().detach().numpy().flatten().tolist()


def norm_padding(padding, out_padding=[0, 0]):
    return [
        padding[0], padding[1], padding[0] - out_padding[0],
        padding[1] - out_padding[1]
    ]


def get_torch_dtype(v):
    if v is not None:
        return [
            torch.uint8, torch.int8, torch.int16, torch.int32, torch.int64,
            torch.float16, torch.float32, torch.float64, torch.complex32,
            torch.complex64, torch.complex128, torch.bool, torch.qint8,
            torch.quint8, torch.qint32, torch.bfloat16
        ][v]
    return v


def get_torch_dtype_string(dt: torch.dtype):
    all_t = [
        torch.uint8, torch.int8, torch.int16, torch.int32, torch.int64,
        torch.float16, torch.float32, torch.float64, torch.complex32,
        torch.complex64, torch.complex128, torch.bool, torch.qint8,
        torch.quint8, torch.qint32, torch.bfloat16
    ]
    all_s = [
        'uint8', 'int8', 'int16', 'int32', 'int64', 'float16', 'float32',
        'float64', 'complex32', 'complex64', 'complex128', 'bool', 'qint8',
        'quint8', 'qint32', 'bfloat16'
    ]
    for t, s in zip(all_t, all_s):
        if t == dt:
            return s
    raise "known torch type"


def get_numpy_dtype(v):
    if v is not None:
        return [
            np.uint8, np.int8, np.int16, np.int32, np.int64, np.float16,
            np.float32, np.float64, None, np.complex64, np.complex128,
            np.bool_, None, None, None, None
        ][int(v)]
    return v


def get_torch_layout(v):
    if v is not None:
        # Strided, Sparse, SparseCsr, Mkldnn, NumOptions
        return [torch.strided, torch.sparse, torch.sparse_csr,
                torch._mkldnn][v]
    return v


def get_torch_memory_format(v):
    if v is not None:
        return [
            torch.contiguous_format, torch.channels_last, torch.preserve_format
        ][v]
    return v


def aten_const_prop(builder, node, namespace, op, *args):
    """
    a function to run contant propagation for aten operators.
    """
    op = op.lower()

    if op == 'rand':
        # aten::rand(int[] size, *, ScalarType? dtype=None, Layout? layout=None, Device? device=None, bool? pin_memory=None) -> Tensor
        return torch.rand(
            *args[0], dtype=get_torch_dtype(args[1]), device=args[3])
    if op == 'randn':
        return torch.randn(
            *args[0], dtype=get_torch_dtype(args[1]), device=args[3])
    if op == 'randint':
        # aten::randint.low_generator(int low, int high, int[] size, *, Generator? generator, ScalarType? dtype=None, Layout? layout=None, Device? device=None, bool? pin_memory=None) -> Tensor
        return torch.randint(
            low=args[0],
            high=args[1],
            size=args[2],
            dtype=get_torch_dtype(args[4]),
            device="cpu")
    if op == 'to':
        if len(args) == 5:
            # aten::to.dtype(Tensor self, ScalarType dtype, bool non_blocking=False, bool copy=False, MemoryFormat? memory_format=None) -> Tensor
            return args[0].to(
                dtype=get_torch_dtype(args[1]),
                non_blocking=args[2],
                copy=args[3],
                memory_format=get_torch_memory_format(args[4]))
        if len(args) == 6:
            # aten::to.device(Tensor self, Device device, ScalarType dtype, bool non_blocking=False, bool copy=False, MemoryFormat? memory_format=None) -> Tensor
            return args[0].to(
                device="cpu",
                dtype=get_torch_dtype(args[2]),
                non_blocking=args[3],
                copy=args[4],
                memory_format=get_torch_memory_format(args[5]))
        if len(args) == 8:
            # aten::to.dtype_layout(Tensor self, *, ScalarType? dtype=Non`e, Layout? layout=None, Device? device=None, bool? pin_memory=None,
            #                       bool non_blocking=False, bool copy=False, MemoryFormat? memory_format=None) -> Tensor
            #return args[0].to(dtype=get_torch_dtype(args[1]), layout=get_torch_layout(args[2]), device=args[3], pin_memory=args[4], non_blocking=args[5], copy=args[6], memory_format=get_torch_memory_format(args[7]))
            return args[0].to(
                dtype=get_torch_dtype(args[1]),
                device="cpu",
                non_blocking=args[5],
                copy=args[6],
                memory_format=get_torch_memory_format(args[7]))
        raise ValueError("unknown aten::to")
    if op == 'sum':
        # aten::sum(Tensor self, *, ScalarType? dtype=None) -> Tensor
        return args[0].sum(dtype=get_torch_dtype(args[1]))
    if op == 'sub':
        # aten::sub.Tensor(Tensor self, Tensor other, *, Scalar alpha=1) -> Tensor
        return torch.sub(args[0], *args[1:-1], alpha=args[-1])
    if op == 'add':
        # aten::add.Tensor(Tensor self, Tensor other, *, Scalar alpha=1) -> Tensor
        return torch.add(args[0], *args[1:-1], alpha=args[-1])
    if op == 'div':
        if len(args) == 2:
            # aten::div.Tensor(Tensor self, Tensor other) -> Tensor
            return torch.divide(args[0], args[1])
        if len(args) == 3:
            # aten::divide.Tensor_mode(Tensor self, Tensor other, *, str? rounding_mode) -> Tensor
            return torch.divide(args[0], args[1], rounding_mode=args[2])
        raise ValueError("unknown aten::div")
    if op == 'zeros_like':
        # aten::zeros_like(Tensor self, *, ScalarType? dtype=None, Layout? layout=None, Device? device=None, bool? pin_memory=None, MemoryFormat? memory_format=None) -> Tensor
        return torch.zeros_like(
            args[0],
            dtype=get_torch_dtype(args[1]),
            layout=get_torch_layout(args[2]),
            device="cpu",
            pin_memory=args[4],
            memory_format=get_torch_memory_format(args[5]))
    if op == 'zeros':
        return torch.zeros(
            args[0], dtype=get_torch_dtype(args[1]), device="cpu")
    if op == 'ones':
        return torch.ones(
            args[0], dtype=get_torch_dtype(args[1]), device="cpu")
    if op == 'cumsum':
        # aten::cumsum(Tensor self, int dim, *, ScalarType? dtype=None) -> Tensor
        return torch.cumsum(args[0], args[1], dtype=get_torch_dtype(args[2]))
    if op == 'slice':
        # aten::slice.Tensor(Tensor(a) self, int dim=0, int? start=None, int? end=None, int step=1) -> Tensor(a)
        dim = args[1]
        start = args[2]
        if start < 0:
            start = args[0].shape[dim] + start
        end = args[3]
        if end < 0:
            end = args[0].shape[dim] + end
        if end == np.iinfo(np.int64).max:
            end = args[0].shape[dim]
        idx = [slice(start, end, args[4])]
        for i in range(dim - 1, -1, -1):
            idx = [slice(args[0].shape[i])] + idx
        return args[0][idx]
    if op == 'arange':
        # aten::arange(Scalar end, *, ScalarType? dtype=None, Layout? layout=None, Device? device=None, bool? pin_memory=None) -> Tensor
        if len(args) == 5:
            return torch.arange(
                args[0], dtype=get_torch_dtype(args[1]), device="cpu")
        # aten::arange.start(Scalar start, Scalar end, *, ScalarType? dtype=None, Layout? layout=None, Device? device=None, bool? pin_memory=None) -> Tensor
        if len(args) == 6:
            return torch.arange(
                args[0], args[1], dtype=get_torch_dtype(args[2]), device="cpu")
        # aten::arange.start_step(Scalar start, Scalar end, Scalar step, *, ScalarType? dtype=None, Layout? layout=None, Device? device=None, bool? pin_memory=None) -> Tensor
        if len(args) == 7:
            return torch.arange(
                args[0],
                args[1],
                args[2],
                dtype=get_torch_dtype(args[3]),
                device="cpu")
        raise ValueError('unknown aten::arange')
    if op == 'expand':
        # aten::expand(Tensor self, int[] size, *, bool implicit) -> Tensor"
        return args[0].expand(size=args[1], implicit=args[2])
    if op == 'linspace':
        # aten::linspace(Scalar start, Scalar end, int? steps=None, *, ScalarType? dtype=None, Layout? layout=None, Device? device=None, bool? pin_memory=None) -> Tensor
        return torch.linspace(
            args[0],
            args[1],
            args[2],
            dtype=get_torch_dtype(args[3]),
            device="cpu",
            pin_memory=args[6])
    if op == 'full':
        # aten::full(int[] size, Scalar fill_value, *, ScalarType? dtype=None, Layout? layout=None, Device? device=None, bool? pin_memory=None) -> Tensor
        return torch.full(
            args[0],
            args[1],
            dtype=get_torch_dtype(args[2]),
            device="cpu",
            pin_memory=args[5],
            requires_grad=False)
    if op == 'full_like':
        # aten::full_like(Tensor self, Scalar fill_value, *, ScalarType? dtype=None, Layout? layout=None, Device? device=None, bool? pin_memory=None, MemoryFormat? memory_format=None) -> Tensor
        return torch.full_like(
            args[0],
            args[1],
            dtype=get_torch_dtype(args[2]),
            device="cpu",
            pin_memory=args[5],
            requires_grad=False)
    if op == 'fill':
        args[0][:] = args[1]
        return args[0]
    if op == 'contiguous':
        # aten::contiguous(Tensor(a) self, *, MemoryFormat memory_format=contiguous_format) -> Tensor(a)
        return args[0].contiguous(
            memory_format=get_torch_memory_format(args[1]))
    if op == 'index':
        # aten::index.Tensor(Tensor self, Tensor?[] indices) -> Tensor
        return args[0][args[1]]
    if op == '__getitem__':
        return args[0][args[1]]
    if op == 'scalarimplicit':
        if 'int' in args[0].dtype.__repr__():
            return int(args[0])
        if 'float' in args[0].dtype.__repr__():
            return float(args[0])
    if op == 'alias':
        return args[0]
    if op == 'int':
        return int(args[0])
    if op == 'copy':
        return args[0].copy_(args[1])
    if op == 'gather':
        return torch.gather(args[0], args[1], args[2], sparse_grad=False)
    if op == 'gelu':
        if len(args) == 1:
            return torch.nn.functional.gelu(args[0])
        elif len(args) == 2:
            return torch.nn.functional.gelu(args[0], approximate=args[1])

    if namespace == 'horizon':
        return getattr(torch.ops.horizon, op)(*args)

    if op == 'view':
        args = [
            t.contiguous() if isinstance(t, torch.Tensor) else t for t in args
        ]

    from torch._C import _nn
    if hasattr(_nn, op):
        return getattr(_nn, op)(*args)

    from torch._C import _TensorBase
    if hasattr(_TensorBase, op):
        # self.where(condition, y) is equivalent to torch.where(condition, self, y)
        if op == 'where':
            assert (args[0].dtype == torch.bool) or (
                args[1].dtype == torch.bool)
            if args[0].dtype == torch.bool:
                new_self = args[1]
                new_args = (args[0], *(args[2:]))
                return getattr(_TensorBase, op)(new_self, *new_args)
        return getattr(_TensorBase, op)(*args)

    from torch._C import _VariableFunctions
    if hasattr(_VariableFunctions, op):
        return getattr(_VariableFunctions, op)(*args)

    if hasattr(torch.ops.aten, op):
        return getattr(torch.ops.aten, op)(*args)

    raise ValueError("unreachable constant propagation: node schema",
                     node.schema())
