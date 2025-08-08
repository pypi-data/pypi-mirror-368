import numpy as np
import torch

from functools import reduce

from hbdk.config import March
from hbdk.torch_script.utils import hbir_base
from hbdk.torch_script.utils import TensorManager as tm
from hbdk.torch_script.utils import get_common_torch_native, get_torch_dtype, aten_const_prop, unwrap_tensor_manager, \
    need_pred, assign_pred, to_hbir_tensor, get_torch_dtype_string, perm_from_native, perm_to_native


def run_pred(builder, ret, namespace, op, args):
    if need_pred(ret):
        args = unwrap_tensor_manager(args)
        ret_sample = aten_const_prop(builder, None, namespace, op, *args)
    else:
        ret_sample = None
    assign_pred(builder, ret, ret_sample)


def aten_alias(builder, annotated_name, node, input):
    return input


def aten_split(builder, annotated_name, node, input, size, dim):
    assert isinstance(input, tm)

    tr = input.retrieve()
    dim = tr.transpose_dim(dim)
    annotated_name = tr.process_name(annotated_name)

    if not isinstance(size, (list, tuple)):
        size = [size] * (tr.shape()[dim] // size)

    if tr.shape()[dim] == size[0]:
        print("WARNING:", annotated_name, "is useless split operation")
        return tuple([input])

    hbirs = hbir_base.CreateSplitLayer(tr.hbir, annotated_name, dim, 0, size,
                                       tr.dtype(), annotated_name)
    return [tm(ir, tr.torch_native) for ir in hbirs]


aten_split_with_sizes = aten_split


def aten_slice(builder, annotated_name, node, input, dim, start, end, step):
    assert isinstance(input, tm)

    if (start == 0) and (end == np.iinfo(np.int64).max) and (step == 1):
        return input

    tr = input.retrieve()
    dim = tr.transpose_dim(dim)
    annotated_name = tr.process_name(annotated_name)

    slice_begin = [0] * len(tr.shape())
    slice_end = tr.shape()
    slice_step = [1] * len(tr.shape())

    slice_begin[dim] = tr.shape()[dim] + start if start < 0 else start
    if end != np.iinfo(np.int64).max:
        slice_end[dim] = tr.shape()[dim] + end if end < 0 else end
    slice_step[dim] = step

    hbir = hbir_base.CreateSliceLayer(tr.hbir, annotated_name,
                                      slice_begin, slice_end, slice_step,
                                      tr.dtype(), annotated_name)
    return tm(hbir, tr.torch_native)


def aten_cat(builder, annotated_name, node, inputs, dim):

    for i in inputs:
        assert isinstance(i, tm)

    if len(inputs) == 1:  # useless concat
        return inputs[0]

    torch_native = get_common_torch_native(
        inputs)  # align multiple TensorManagers
    trs = [tm.retrieve(torch_native) for tm in inputs]
    dim = trs[0].transpose_dim(dim)
    annotated_name = trs[0].process_name(annotated_name)
    hbir = hbir_base.CreateConcatLayer([tr.hbir for tr in trs], annotated_name,
                                       dim, trs[0].dtype(), annotated_name)
    return tm(hbir, torch_native)


def aten_relu(builder, annotated_name, node, input):
    tr = input.retrieve()
    annotated_name = tr.process_name(annotated_name)
    assert isinstance(input, tm)
    hbir = hbir_base.CreateReluLayer(tr.hbir, annotated_name, tr.dtype(),
                                     annotated_name)
    return tm(hbir, tr.torch_native)


def _max_like(builder,
              annotated_name,
              node,
              input,
              dim,
              keep_dim,
              bernoulli_keep_val_arg=()):
    assert isinstance(input, tm)
    assert len(
        bernoulli_keep_val_arg
    ) > 1, annotated_name + " length of bernoulli_keep_val_arg should larger than 1"
    assert keep_dim == True, "only supports 4d tensor. reducing dim is not allowed"

    if builder.march_enum in [March.BERNOULLI2, March.BERNOULLI]:
        assert bernoulli_keep_val_arg[0] or bernoulli_keep_val_arg[1]
        sample_in_hardware = None

        tr = input.retrieve(torch_native=False)
        annotated_name = tr.process_name(annotated_name)

        if builder.run_pred:
            val, arg = torch.max(input.native_sample, dim, keep_dim)
            if bernoulli_keep_val_arg[0] and bernoulli_keep_val_arg[1]:
                sample_in_hardware = torch.cat([arg, val], dim)
            elif bernoulli_keep_val_arg[0]:
                sample_in_hardware = torch.cat([val], dim)
            elif bernoulli_keep_val_arg[1]:
                sample_in_hardware = torch.cat([arg], dim)

        dim = tr.transpose_dim(dim)
        assert dim == 3, "only supports channel max/argmax"

        ret = hbir_base.CreateChannelMax(
            tr.hbir, annotated_name, bernoulli_keep_val_arg[0],
            bernoulli_keep_val_arg[1], False, 0, 1, annotated_name)

        return [
            tm(ret, tr.torch_native, sample_in_hardware),
            tm(ret, tr.torch_native, sample_in_hardware)
        ]

    elif (builder.march_enum == March.BAYES or builder.march_enum == March.B25E
          or builder.march_enum == March.B253):
        tr = input.retrieve()
        annotated_name = tr.process_name(annotated_name)

        dim = tr.transpose_dim(dim)
        hbir = tr.hbir
        min_val = hbir_base.CreateReduceMaxLayer(
            hbir, annotated_name + "_get_val", dim, False,
            annotated_name + "_val")
        min_arg = hbir_base.CreateReduceMaxLayer(
            hbir, annotated_name + "_get_arg", dim, True,
            annotated_name + "_arg")
        return [tm(min_val, tr.torch_native), tm(min_arg, tr.torch_native)]

    else:
        tr = input.retrieve(torch_native=False)
        annotated_name = tr.process_name(annotated_name)

        dim = tr.transpose_dim(dim)
        assert dim == 3, "only supports channel max/argmax"
        ret = hbir_base.CreateChannelMax(tr.hbir, annotated_name + "_bpu_max",
                                         True, True, False, 0, 1,
                                         annotated_name)
        shape = hbir_base.GetTensorShape(ret)
        assert len(
            shape) == 4, annotated_name + " only support 4-dimensional tensor"
        assert shape[-1] == 2
        max_arg = hbir_base.CreateSliceLayer(
            ret, annotated_name + "_get_arg",
            [0, 0, 0, 0], [shape[0], shape[1], shape[2], 1], [1, 1, 1, 1],
            tr.dtype(), annotated_name + "_arg")
        max_val = hbir_base.CreateSliceLayer(
            ret, annotated_name + "_get_val",
            [0, 0, 0, 1], [shape[0], shape[1], shape[2], 2], [1, 1, 1, 1],
            tr.dtype(), annotated_name + "_val")
        return [tm(max_val, tr.torch_native), tm(max_arg, tr.torch_native)]


def _min_like(builder, annotated_name, node, input, dim, keep_dim):
    assert isinstance(input, tm)
    assert keep_dim == True, "only supports 4d tensor. reducing dim is not allowed"
    assert builder.march_enum == March.BAYES or builder.march_enum == March.B25E or builder.march_enum == March.B253, "only support b25 now"

    tr = input.retrieve(torch_native=False) \
        if len(input.records[0].shape()) > 2 else input.retrieve(torch_native=True)
    annotated_name = tr.process_name(annotated_name)

    dim = tr.transpose_dim(dim) if len(input.records[0].shape()) > 2 else dim
    hbir = tr.hbir
    min_val = hbir_base.CreateReduceMinLayer(
        hbir, annotated_name + "_get_val", dim, False, annotated_name + "_val")
    min_arg = hbir_base.CreateReduceMinLayer(
        hbir, annotated_name + "_get_arg", dim, True, annotated_name + "_arg")

    return [tm(min_val, tr.torch_native), tm(min_arg, tr.torch_native)]


def aten_max(builder, annotated_name, node, input, dim, keep_dim):
    return _max_like(builder, annotated_name, node, input, dim, keep_dim,
                     (True, True))


def aten_argmax(builder, annotated_name, node, input, dim, keep_dim):
    ret = _max_like(builder, annotated_name, node, input, dim, keep_dim,
                    (False, True))
    return ret[-1]


def aten_amax(builder, annotated_name, node, input, dim, keep_dim):
    if isinstance(dim, list):
        assert len(dim) == 1
        dim = dim[0]
    ret = _max_like(builder, annotated_name, node, input, dim, keep_dim,
                    (True, False))
    return ret[0]


def aten_min(builder, annotated_name, node, input, dim, keep_dim):
    return _min_like(builder, annotated_name, node, input, dim, keep_dim)


def aten_argmin(builder, annotated_name, node, input, dim, keep_dim):
    ret = _min_like(builder, annotated_name, node, input, dim, keep_dim)
    return ret[-1]


def aten_amin(builder, annotated_name, node, input, dim, keep_dim):
    if isinstance(dim, list):
        assert len(dim) == 1
        dim = dim[0]
    ret = _min_like(builder, annotated_name, node, input, dim, keep_dim)
    return ret[0]


def _reshape_like(builder, annotated_name, node, input, shape):
    # shape canonicalization.
    tr = input.retrieve(torch_native=True)
    annotated_name = tr.process_name(annotated_name)
    input_shape = tr.shape()

    # assert (len(input_shape) == 4) and (
    #     len(shape) == 4), "input and shape for reshape must be dims of 4."

    import functools
    input_elements = functools.reduce(lambda x, y: x * y, input_shape)
    target_elements = 1
    negative_index = []
    for idx in range(0, len(shape)):
        assert (shape[idx] > 0) or (
            shape[idx] == -1), "shape for reshape must be positive or -1."
        if shape[idx] > 0:
            target_elements *= shape[idx]
        else:
            negative_index.append(idx)
    assert (len(negative_index) <=
            1), "shape for reshape cannot contain more than one -1."
    if len(negative_index):
        shape[negative_index[0]] = int(input_elements / target_elements)
        target_elements = input_elements
    assert (target_elements == input_elements
            ), "elements num before and after reshape must be equal."

    hbir = hbir_base.CreateViewLayer(tr.hbir, annotated_name, shape,
                                     annotated_name)
    return tm(hbir, torch_native=True)


def aten_reshape(*args):
    # "at::Tensor at::reshape(const at::Tensor &self, at::IntArrayRef shape)"
    return _reshape_like(*args)


def aten_view(*args):
    return _reshape_like(*args)


def _transpose_like(builder, annotated_name, node, input, perm):
    tr = input.retrieve()
    annotated_name = tr.process_name(annotated_name)
    if not tr.torch_native and tr.rank() > 2:
        hbir_native_dim_idx = [i for i in range(0, tr.rank())]
        torch_native_dim_idx = [
            hbir_native_dim_idx[i] for i in perm_to_native(tr.rank())
        ]
        torch_native_dim_idx = [torch_native_dim_idx[i]
                                for i in perm]  # after transpose
        hbir_native_dim_idx = [
            torch_native_dim_idx[i] for i in perm_from_native(tr.rank())
        ]
        perm = hbir_native_dim_idx

    hbir = hbir_base.CreateTransposeLayer(tr.hbir, annotated_name, perm,
                                          annotated_name)
    return tm(hbir, torch_native=tr.torch_native)


def aten_transpose(builder, annotated_name, node, input, dim0, dim1):
    dims = [i for i in range(input.retrieve().rank())]
    dims[dim0], dims[dim1] = dims[dim1], dims[dim0]
    return _transpose_like(builder, annotated_name, node, input, dims)


def aten_permute(builder, annotated_name, node, input, dims):
    return _transpose_like(builder, annotated_name, node, input, dims)


def aten_zeros_like(builder, annotated_name, node, input, dtype, layout,
                    device, pin_memory, memory_format):
    tr = input.retrieve(torch_native=True)
    return torch.zeros(
        tr.shape(),
        dtype=get_torch_dtype(dtype),
        device=device,
        pin_memory=pin_memory)


def aten_ones_like(builder, annotated_name, node, input, dtype, layout, device,
                   pin_memory, memory_format):
    tr = input.retrieve(torch_native=True)
    return torch.ones(
        tr.shape(),
        dtype=get_torch_dtype(dtype),
        device=device,
        pin_memory=pin_memory)


def aten_size(builder, annotated_name, node, input, dim):
    tr = input.retrieve()
    return tr.shape()[tr.transpose_dim(dim)]


def aten_contiguous(builder, annotated_name, node, input, layout):
    if isinstance(input, torch.Tensor):
        return input.contiguous()
    return input


def aten___getitem__(builder, annotated_name, node, map, key):
    assert isinstance(map, dict)
    return map[key]


def aten_detach(builder, annotated_name, node, input):
    if isinstance(input, torch.Tensor):
        return input.detach()
    return input


def aten_dropout(builder, annotated_name, node, input, p, train):
    # aten::dropout(Tensor input, float p, bool train) -> Tensor
    if train:
        raise ValueError("dropout training mode is not supported")
    return input  # meaningless for hbdk


def _clamp_like(builder, annotated_name, node, input, min, max, dtype):
    tr = input.retrieve()
    annotated_name = tr.process_name(annotated_name)
    int_max = 2147483647
    min_val = int_max
    max_val = int_max
    min_tensor = ''
    max_tensor = ''
    if isinstance(min, int):
        min_val = min
    elif isinstance(min, str):
        min_tensor = min
    if isinstance(max, int):
        max_val = max
    elif isinstance(max, str):
        max_tensor = max
    hbir = hbir_base.CreateClampLayer(tr.hbir, min_tensor, max_tensor,
                                      annotated_name, min_val, max_val, dtype,
                                      annotated_name)
    return tm(hbir, tr.torch_native)


def aten_clamp(builder, annotated_name, node, input, min, max):
    # https://pytorch.org/docs/stable/generated/torch.clamp.html#torch.clamp
    tr = input.retrieve()
    dtype = tr.dtype()
    return _clamp_like(builder, annotated_name, node, input, min, max, dtype)


def aten_clip(*args):
    # https://pytorch.org/docs/stable/generated/torch.clip.html#torch.clip
    return aten_clamp(*args)


def _ew_compare_like(func, builder, annotated_name, node, lhs, rhs):
    torch_native = get_common_torch_native(
        [lhs, rhs])  # align multiple TensorManagers

    if isinstance(lhs, torch.Tensor):
        lhs, = to_hbir_tensor([lhs], annotated_name,
                              [get_torch_dtype_string(lhs.dtype)],
                              torch_native)
    if isinstance(rhs, torch.Tensor):
        rhs, = to_hbir_tensor([rhs], annotated_name,
                              [get_torch_dtype_string(rhs.dtype)],
                              torch_native)

    assert isinstance(lhs, tm)
    assert isinstance(rhs, tm)

    trs = [tm.retrieve(torch_native) for tm in [lhs, rhs]]
    assert len(trs) == 2
    annotated_name = trs[0].process_name(annotated_name)
    hbir = func([tr.hbir for tr in trs], annotated_name, annotated_name)
    return tm(hbir, torch_native)


def aten_eq(builder, annotated_name, node, lhs, rhs):
    return _ew_compare_like(hbir_base.CreateElementwiseEqual, builder,
                            annotated_name, node, lhs, rhs)


def aten_ne(builder, annotated_name, node, lhs, rhs):
    return _ew_compare_like(hbir_base.CreateElementwiseNotEqual, builder,
                            annotated_name, node, lhs, rhs)


def aten_lt(builder, annotated_name, node, lhs, rhs):
    return _ew_compare_like(hbir_base.CreateElementwiseLess, builder,
                            annotated_name, node, lhs, rhs)


def aten_le(builder, annotated_name, node, lhs, rhs):
    return _ew_compare_like(hbir_base.CreateElementwiseLessOrEqual, builder,
                            annotated_name, node, lhs, rhs)


def aten_gt(builder, annotated_name, node, lhs, rhs):
    return _ew_compare_like(hbir_base.CreateElementwiseGreater, builder,
                            annotated_name, node, lhs, rhs)


def aten_ge(builder, annotated_name, node, lhs, rhs):
    return _ew_compare_like(hbir_base.CreateElementwiseGreaterOrEqual, builder,
                            annotated_name, node, lhs, rhs)


def aten_maximum(builder, annotated_name, node, lhs, rhs):
    return _ew_compare_like(hbir_base.CreateElementwiseMax, builder,
                            annotated_name, node, lhs, rhs)


def aten_minimum(builder, annotated_name, node, lhs, rhs):
    return _ew_compare_like(hbir_base.CreateElementwiseMin, builder,
                            annotated_name, node, lhs, rhs)


def _tile_like(builder, annotated_name, node, input, dims):
    tr = input.retrieve()
    input_shape = tr.shape()
    annotated_name = tr.process_name(annotated_name)

    if len(input_shape) < len(dims):
        # unsqueeze
        new_input_shape = [1] * (len(dims) - len(input_shape)) + input_shape
        input = aten_reshape(builder, annotated_name + '_inc_dim', node, input,
                             new_input_shape)

    tr = input.retrieve()
    input_shape = tr.shape()
    annotated_name = tr.process_name(annotated_name)

    dims = [1] * (len(input_shape) - len(dims)) + dims

    # Process one dimension at a time
    process_list = []
    for i, dim in enumerate(dims):
        if dim == 1:
            continue
        i = tr.transpose_dim(i)
        process_list += [[i, dim, "_pre_dim%d" % i]]
    assert len(process_list) > 0
    process_list[-1][-1] = ""

    tr_hbir = tr.hbir
    for (i, dim, suffix) in process_list:
        tr_hbir = hbir_base.CreateTileLayer(tr_hbir, annotated_name + suffix,
                                            i, dim, annotated_name + suffix)

    return tm(tr_hbir, tr.torch_native)


def aten_tile(*args):
    # https://pytorch.org/docs/stable/generated/torch.tile.html#torch-tile
    return _tile_like(*args)


def aten_repeat(*args):
    # https://pytorch.org/docs/stable/generated/torch.Tensor.repeat.html#torch-tensor-repeat
    return _tile_like(*args)


def aten_expand(builder, annotated_name, node, input, sizes, implicit):
    # https://pytorch.org/docs/stable/generated/torch.Tensor.expand.html#torch-tensor-expand
    # https://pytorch.org/docs/stable/jit_builtin_functions.html?highlight=aten%20expand
    tr = input.retrieve()
    input_shape = tr.shape()
    annotated_name = tr.process_name(annotated_name)

    if len(input_shape) > len(sizes):
        raise ValueError(
            "the number of sizes provided (%d) must be greater or equal to the number of "
            "dimensions in the tensor (%d)" % (len(sizes), len(input_shape)))

    if len(input_shape) < len(sizes):
        # unsqueeze
        new_input_shape = [1] * (len(sizes) - len(input_shape)) + input_shape
        input = aten_reshape(builder, annotated_name + '_inc_dim', node, input,
                             new_input_shape)

    tr = input.retrieve()
    input_shape = input.retrieve(torch_native=True).shape()
    annotated_name = tr.process_name(annotated_name)

    dims = []
    for a, b in zip(input_shape, sizes):
        if a != 1 and a != b and b != -1:
            raise ValueError(
                "The expanded size of the tensor (%d) must match the existing size (%d) at non-singleton dimension 0."
                % (a, b))
        if b > a and a == 1:
            dims += [b]
        else:
            dims += [1]

    # Process one dimension at a time
    process_list = []
    for i, dim in enumerate(dims):
        if dim == 1:
            continue
        i = tr.transpose_dim(i)
        process_list += [[i, dim, "_pre_dim%d" % i]]
    assert len(process_list) > 0
    process_list[-1][-1] = ""

    tr_hbir = tr.hbir
    for (i, dim, suffix) in process_list:
        tr_hbir = hbir_base.CreateTileLayer(tr_hbir, annotated_name + suffix,
                                            i, dim, annotated_name + suffix)

    return tm(tr_hbir, tr.torch_native)


def aten_squeeze(builder, annotated_name, node, input, dim=None):
    # https://pytorch.org/docs/stable/generated/torch.squeeze.html#torch-squeeze
    tr = input.retrieve(torch_native=True)
    input_shape = tr.shape()
    annotated_name = tr.process_name(annotated_name)

    output_shape = []
    if dim is None:
        for i in input_shape:
            if i > 1:
                output_shape += [i]
    else:
        dim = tr.transpose_dim(dim)
        if input_shape[dim] == 1:
            output_shape = input_shape[:dim] + input_shape[dim + 1:]
        else:
            output_shape = input_shape

    if output_shape == input_shape:
        return input
    return aten_reshape(builder, annotated_name, node, input, output_shape)


def aten_unsqueeze(builder, annotated_name, node, input, dim):
    # https://pytorch.org/docs/stable/generated/torch.unsqueeze.html#torch-unsqueeze
    tr = input.retrieve(torch_native=True)
    input_shape = tr.shape()
    annotated_name = tr.process_name(annotated_name)

    assert dim in range(-tr.rank() - 1, tr.rank() + 1)
    if dim < 0:
        dim += tr.rank() + 1
    output_shape = input_shape[:dim] + [1] + input_shape[dim:]

    return aten_reshape(builder, annotated_name, node, input, output_shape)


def aten_flatten(builder, annotated_name, node, input, start_dim, end_dim):
    # https://pytorch.org/docs/stable/generated/torch.flatten.html#torch-flatten
    tr = input.retrieve(torch_native=True)
    input_shape = tr.shape()
    annotated_name = tr.process_name(annotated_name)

    assert start_dim in range(-tr.rank(), tr.rank())
    if start_dim < 0:
        start_dim += tr.rank()
    assert end_dim in range(-tr.rank(), tr.rank())
    if end_dim < 0:
        end_dim += tr.rank()
    assert start_dim <= end_dim
    output_shape = input_shape[:start_dim] + [
        reduce(lambda x, y: x * y, input_shape[start_dim:end_dim + 1])
    ] + input_shape[end_dim + 1:]

    if output_shape == input_shape:
        return input
    return aten_reshape(builder, annotated_name, node, input, output_shape)


def aten_pixel_shuffle(builder, annotated_name, node, input, upscale_factor):
    # https://pytorch.org/docs/stable/nn.functional.html#nn.functional.pixel_shuffle
    tr = input.retrieve(torch_native=False)
    input_shape = tr.shape()
    annotated_name = tr.process_name(annotated_name)
    output_shape = []
    upscale_vector = [upscale_factor, upscale_factor]
    assert len(input_shape) == 4
    tr_hbir = hbir_base.CreateReshapeLayer(
        tr.hbir, annotated_name, "reorder_upscale_unfold", output_shape,
        tr.dtype(), annotated_name, upscale_vector)
    return tm(tr_hbir, tr.torch_native)


def aten_pixel_unshuffle(builder, annotated_name, node, input,
                         downscale_factor):
    # https://pytorch.org/docs/stable/generated/torch.nn.PixelShuffle.html#torch.nn.PixelShuffle
    tr = input.retrieve(torch_native=False)
    input_shape = tr.shape()
    annotated_name = tr.process_name(annotated_name)
    output_shape = []
    downscale_vector = [downscale_factor, downscale_factor]
    assert len(input_shape) == 4
    tr_hbir = hbir_base.CreateReshapeLayer(
        tr.hbir, annotated_name, "stack_neighbor_interleaved", output_shape,
        tr.dtype(), annotated_name, downscale_vector)
    return tm(tr_hbir, tr.torch_native)


def aten_roll(builder, annotated_name, node, input, shifts, dims):
    assert len(shifts) == len(
        dims), +annotated_name + "size of shifts and dims should be the same"

    tr = input.retrieve(torch_native=True)
    annotated_name = tr.process_name(annotated_name)

    inShape = tr.shape()
    shifts = [(shifts[i] + inShape[dims[i]]) % inShape[dims[i]]
              for i in range(0, len(dims))]

    tr_hbir = hbir_base.CreateRollLayer(tr.hbir, shifts, dims, annotated_name,
                                        annotated_name)
    return tm(tr_hbir, tr.torch_native)


def aten_gather(bulder,
                annotated_name,
                node,
                input,
                dim,
                indices,
                sparse_grad=False):
    # https://pytorch.org/docs/stable/generated/torch.gather.html?highlight=gather#torch.gather
    assert sparse_grad == False, "support sparse_grad=False only"

    tr = input.retrieve(torch_native=True)
    annotated_name = tr.process_name(annotated_name)
    tr_idx = indices.retrieve(torch_native=True)

    hbir = hbir_base.CreateGatherElementsLayer(
        tr.hbir, tr_idx.hbir, annotated_name, dim, annotated_name)
    return tm(hbir, tr.torch_native)
