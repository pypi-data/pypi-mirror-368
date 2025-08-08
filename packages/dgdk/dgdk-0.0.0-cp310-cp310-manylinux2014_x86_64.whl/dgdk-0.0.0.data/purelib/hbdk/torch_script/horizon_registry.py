import numpy as np

from typing import Optional, Tuple

from hbdk.config import March

from hbdk.torch_script.utils import hbir_base  # avoid multiple imports
from hbdk.torch_script.utils import TensorManager as tm
from hbdk.torch_script.utils import torch_tensor_to_list, gen_rescale_param, to_hbir_tensor, get_common_torch_native, \
    unwrap_tensor_manager, need_pred, assign_pred, get_torch_dtype, get_torch_dtype_string, get_numpy_dtype

import torch
import horizon_plugin_pytorch.nn.functional as hf
import horizon_plugin_pytorch.nn.quantized.functional as hqf
import horizon_plugin_pytorch.nn.functional as hff


def run_pred(builder, ret, func, raw_args):
    ret_sample = None
    if need_pred(ret):
        args = unwrap_tensor_manager(raw_args)
        assert len(args), "args is empty"
        if hasattr(hqf, func):
            if func == 'rle':
                args[1] = get_torch_dtype(args[1])
            ret_sample = getattr(hqf, func)(*args)
        if hasattr(hf, func):
            ret_sample = getattr(hf, func)(*args)
        if hasattr(hff, func):
            ret_sample = getattr(hf, func)(*args)
        if ret_sample is None:
            raise ValueError("unknown pred", func)
    assign_pred(builder, ret, ret_sample)


def quantize(builder, annotated_name, node, input, scale, zero, axis, dtype,
             march):
    if len(scale) != 1:
        raise ValueError("only per-tensor quantize is supported")
    assert isinstance(input, tm)
    if builder.march_enum == March.BERNOULLI:
        input.shift(scale)
    else:
        input.scale(scale)
    input.dtype(dtype[1:])  # horizon plugin starts with 'q'
    if builder.run_pred:  # override input
        if input.native_sample.dtype == torch.float:
            input.native_sample = hqf.quantize(input.native_sample, scale,
                                               zero, axis, dtype, march)
    return input


def dequantize(builder, annotated_name, node, *args):
    assert len(
        args) >= 4, annotated_name + "there are at least 4 parameters in args"
    input = args[0]
    scale = args[1]
    zero = args[2]
    march = args[-1]
    assert isinstance(input, tm)
    if builder.march_enum == March.BERNOULLI:
        input.shift(scale)
    else:
        input.scale(scale)
    return input


def requantize(builder,
               annotated_name,
               node,
               input,
               iscale,
               izero,
               itype,
               oscale,
               ozero,
               otype,
               march,
               torch_native=None,
               enable_rounding=True):
    if torch.equal(iscale, oscale) and itype == otype:
        print("WARNING:", annotated_name, "is useless. iscale vs. oscale: ",
              iscale, ",", oscale)
        return input

    assert len(izero) and izero[
        0] == 0, annotated_name + "izero shouldn't be empty, and izero[0] should equal to 0"
    assert len(ozero) and ozero[
        0] == 0, annotated_name + "ozero shouldn't be empty, and ozero[0] should equal to 0"

    if isinstance(input, torch.Tensor):
        return hqf.requantize(input, iscale, izero, itype, oscale, ozero,
                              otype, march)

    tr = input.retrieve(torch_native)
    annotated_name = tr.process_name(annotated_name)
    assert len(tr.shape(
    )), annotated_name + "the input tensor' shape should at least be 1"
    channel = tr.shape()[-1]
    qscale, post_rshift, pre_rshift = gen_rescale_param(
        iscale, itype[1:], oscale, otype[1:], builder.march_enum)
    assert pre_rshift == 0
    hbir = hbir_base.CreateRescale(tr.hbir, annotated_name,
                                   qscale.tolist() * channel,
                                   post_rshift.tolist() * channel, otype[1:],
                                   annotated_name, enable_rounding)
    return tm(hbir, tr.torch_native)


def conv2d(builder, annotated_name, node, input, weight, bias, sumin, stride,
           padding, dilation, groups, padding_mode, activation, input_scale,
           input_zero_point, input_dtype, weight_scale, weight_zero_point,
           weight_dtype, bias_scale, bias_zero_point, bias_dtype, sumin_scale,
           sumin_zero_point, sumin_dtype, scale, zero_point, dtype, march):
    assert isinstance(input, tm)
    assert len(weight.size()
               ) == 4, annotated_name + "size of the weight should equal to 4"
    tr = input.retrieve(torch_native=False)
    annotated_name = tr.process_name(annotated_name)

    filters = weight.size()[0]
    kernel = (weight.size()[2], weight.size(3))
    weight_name = annotated_name + "_weight"  # shall not use NamedAttr name because iscale might be different and the deduced bias is different!
    bias_name = annotated_name + "_bias"

    from horizon_plugin_pytorch.nn.quantized.functional import conv2d_convert_int_params

    if builder.march_enum == March.BERNOULLI:
        (bpu_weight, bpu_weight_shift, bpu_bias, bpu_bias_shift,
         bpu_input_shift, bpu_output_shift, bpu_edata_shift,
         dequant_output_scale, _) = conv2d_convert_int_params(
             input_scale, weight, weight_scale, weight_dtype, bias, bias_scale,
             bias_dtype, scale, dtype,
             sumin_scale if sumin is not None else None, False, groups, march)
        bpu_weight = torch.permute(
            bpu_weight, [0, 2, 3, 1])  # from cout,cin,kh,kw to cout,kh,kw,cin
        hbir = hbir_base.CreateConvolutionLayer(
            tr.hbir, annotated_name, filters, kernel, stride, padding,
            dilation, groups, True, activation == "relu",
            sumin.retrieve(
                torch_native=False).hbir if sumin is not None else "null",
            dtype[1:], annotated_name, "int8", weight_name,
            torch_tensor_to_list(bpu_weight), bias_name,
            torch_tensor_to_list(bpu_bias),
            False)  # pylint: disable-msg=too-many-arguments

        input.shift(bpu_input_shift)
        hbir_base.SetTensorShift(weight_name,
                                 torch_tensor_to_list(bpu_weight_shift))
        hbir_base.SetTensorShift(bias_name,
                                 torch_tensor_to_list(bpu_bias_shift))
        if dtype[1:] == "int8":
            hbir_base.SetTensorShift(hbir,
                                     torch_tensor_to_list(bpu_output_shift))
        if sumin != None:
            sumin.shift(bpu_edata_shift)
        return tm(hbir, tr.torch_native), dequant_output_scale

    (bpu_weight, bpu_bias, bpu_bias_lshift, bpu_escale, bpu_escale_lshift,
     bpu_oscale, bpu_accu_rshift, bpu_output_rshift,
     dequant_output_scale) = conv2d_convert_int_params(
         input_scale, weight, weight_scale, weight_dtype, bias, bias_scale,
         bias_dtype, scale, dtype, sumin_scale if sumin is not None else None,
         False, groups, march)

    enable_rounding = (builder.march_enum == March.BAYES
                       or builder.march_enum == March.B25E
                       or builder.march_enum == March.B253)

    bpu_weight = torch.permute(
        bpu_weight, [0, 2, 3, 1])  # from cout,cin,kh,kw to cout,kh,kw,cin

    if dtype == 'qint32':  # disable output rescale
        bpu_accu_rshift = []
        bpu_oscale = []
        bpu_output_rshift = torch.zeros(filters, dtype=torch.int32)
    if sumin == None:
        bpu_escale = []
        bpu_escale_lshift = []
    else:
        sumin, = to_hbir_tensor([sumin], annotated_name + "_weight",
                                [sumin_dtype], False)
        sumin = sumin.retrieve(torch_native=False)

    hbir = hbir_base.CreateSConvolutionLayer(
        tr.hbir, annotated_name, filters, kernel, stride, padding, dilation,
        groups, True, activation == "relu",
        sumin.hbir if sumin is not None else "null", dtype[1:], annotated_name,
        weight_name, torch_tensor_to_list(bpu_weight), bias_name,
        torch_tensor_to_list(bpu_bias), enable_rounding,
        torch_tensor_to_list(bpu_accu_rshift),
        torch_tensor_to_list(bpu_bias_lshift),
        torch_tensor_to_list(bpu_oscale),
        torch_tensor_to_list(bpu_output_rshift),
        torch_tensor_to_list(bpu_escale),
        torch_tensor_to_list(
            bpu_escale_lshift))  # pylint: disable-msg=too-many-arguments
    return tm(hbir, tr.torch_native), dequant_output_scale


def conv3d(builder, annotated_name, node, input, weight, bias, sumin, stride,
           padding, dilation, groups, padding_mode, activation, input_scale,
           input_zero_point, input_dtype, weight_scale, weight_zero_point,
           weight_dtype, bias_scale, bias_zero_point, bias_dtype, sumin_scale,
           sumin_zero_point, sumin_dtype, scale, zero_point, dtype, march):
    assert isinstance(input, tm)
    assert len(weight.size()
               ) == 5, annotated_name + "size of the weight should equal to 5"
    tr = input.retrieve(torch_native=False)
    annotated_name = tr.process_name(annotated_name)

    filters = weight.size()[0]

    kernel = (weight.size()[2], weight.size(3), weight.size()[4])
    weight_name = annotated_name + "_weight"  # shall not use NamedAttr name because iscale might be different and the deduced bias is different!
    bias_name = annotated_name + "_bias"

    from horizon_plugin_pytorch.nn.quantized.functional import conv2d_convert_int_params

    (bpu_weight, bpu_bias, bpu_bias_lshift, bpu_escale, bpu_escale_lshift,
     bpu_oscale, bpu_accu_rshift, bpu_output_rshift,
     dequant_output_scale) = conv2d_convert_int_params(
         input_scale, weight, weight_scale, weight_dtype, bias, bias_scale,
         bias_dtype, scale, dtype, sumin_scale if sumin is not None else None,
         False, groups, march)

    enable_rounding = (builder.march_enum == March.BAYES
                       or builder.march_enum == March.B25E
                       or builder.march_enum == March.B253)
    bpu_weight = torch.permute(
        bpu_weight, [0, 2, 3, 4, 1])  # from cout,cin,kh,kw to cout,kh,kw,cin

    if dtype == 'qint32':  # disable output rescale
        bpu_accu_rshift = []
        bpu_oscale = []
        bpu_output_rshift = torch.zeros(filters, dtype=torch.int32)
    if sumin == None:
        bpu_escale = []
        bpu_escale_lshift = []
    else:
        sumin = sumin.retrieve(torch_native=False)
    hbir = hbir_base.CreateConv3dLayer(
        tr.hbir, annotated_name, kernel, stride, padding, dilation, filters,
        groups, True, activation == "relu",
        sumin.hbir if sumin is not None else "null", weight_name,
        torch_tensor_to_list(bpu_weight), bias_name,
        torch_tensor_to_list(bpu_bias), annotated_name, dtype[1:],
        enable_rounding, torch_tensor_to_list(bpu_bias_lshift),
        torch_tensor_to_list(bpu_oscale),
        torch_tensor_to_list(bpu_accu_rshift),
        torch_tensor_to_list(bpu_escale),
        torch_tensor_to_list(bpu_escale_lshift),
        torch_tensor_to_list(bpu_output_rshift))
    return tm(hbir, tr.torch_native), dequant_output_scale


def conv_transpose2d(builder, annotated_name, node, input, weight, bias, sumin,
                     stride, padding, output_padding, dilation, groups,
                     padding_mode, activation, input_scale, input_zero_point,
                     input_dtype, weight_scale, weight_zero_point,
                     weight_dtype, bias_scale, bias_zero_point, bias_dtype,
                     sumin_scale, sumin_zero_point, sumin_dtype, scale,
                     zero_point, dtype, march):
    assert isinstance(input, tm)
    assert len(weight.size()
               ) == 4, annotated_name + "size of the weight should equal to 4 "
    assert (dilation[0] == 1) and (
        dilation[1] == 1), "dilated conv2d transpose is not supported"
    tr = input.retrieve(torch_native=False)
    annotated_name = tr.process_name(annotated_name)

    filters = weight.size()[1] * groups
    kernel = (weight.size()[2], weight.size(3))
    weight_name = annotated_name + "_weight"  # shall not use NamedAttr name because iscale might be different and the deduced bias is different!
    bias_name = annotated_name + "_bias"

    from horizon_plugin_pytorch.nn.quantized.functional import conv2d_convert_int_params

    if builder.march_enum == March.BERNOULLI:
        (bpu_weight, bpu_weight_shift, bpu_bias, bpu_bias_shift,
         bpu_input_shift, bpu_output_shift, bpu_edata_shift,
         dequant_output_scale, _) = conv2d_convert_int_params(
             input_scale, weight, weight_scale, weight_dtype, bias, bias_scale,
             bias_dtype, scale, dtype,
             sumin_scale if sumin is not None else None, True, groups, march)
        bpu_weight = torch.permute(
            bpu_weight, [0, 2, 3, 1])  # from cout,cin,kh,kw to cout,kh,kw,cin
        hbir = hbir_base.CreateDeconvolutionLayer(
            tr.hbir, annotated_name, filters, kernel, stride, padding,
            output_padding, groups, True, activation == "relu",
            sumin.retrieve(
                torch_native=False).hbir if sumin is not None else "null",
            dtype[1:], annotated_name, "int8", weight_name,
            torch_tensor_to_list(bpu_weight), bias_name,
            torch_tensor_to_list(bpu_bias),
            False)  # pylint: disable-msg=too-many-arguments

        input.shift(bpu_input_shift)
        hbir_base.SetTensorShift(weight_name,
                                 torch_tensor_to_list(bpu_weight_shift))
        hbir_base.SetTensorShift(bias_name,
                                 torch_tensor_to_list(bpu_bias_shift))
        if sumin != None:
            sumin.shift(bpu_edata_shift)
        return tm(hbir, tr.torch_native), dequant_output_scale

    (bpu_weight, bpu_bias, bpu_bias_lshift, bpu_escale, bpu_escale_lshift,
     bpu_oscale, bpu_accu_rshift, bpu_output_rshift,
     dequant_output_scale) = conv2d_convert_int_params(
         input_scale, weight, weight_scale, weight_dtype, bias, bias_scale,
         bias_dtype, scale, dtype, sumin_scale if sumin is not None else None,
         True, groups, march)

    enable_rounding = (builder.march_enum == March.BAYES
                       or builder.march_enum == March.B25E
                       or builder.march_enum == March.B253)

    bpu_weight = torch.permute(
        bpu_weight, [0, 2, 3, 1])  # from cin,cout,kh,kw to cin,kh,kw,cout

    if dtype == 'qint32':  # disable output rescale
        bpu_accu_rshift = []
        bpu_oscale = []
        bpu_output_rshift = np.zeros(filters, dtype=np.int32).tolist()
    if sumin == None:
        bpu_escale = []
        bpu_escale_lshift = []
    else:
        assert isinstance(sumin, tm)
        sumin = sumin.retrieve(torch_native=False)

    hbir = hbir_base.CreateSDeconvolutionLayer(
        tr.hbir, annotated_name, filters, kernel, stride, padding,
        output_padding, groups, True, activation == "relu",
        sumin.hbir if sumin is not None else "null", dtype[1:], annotated_name,
        weight_name, torch_tensor_to_list(bpu_weight), bias_name,
        torch_tensor_to_list(bpu_bias), enable_rounding,
        torch_tensor_to_list(bpu_accu_rshift),
        torch_tensor_to_list(bpu_bias_lshift),
        torch_tensor_to_list(bpu_oscale),
        torch_tensor_to_list(bpu_output_rshift),
        torch_tensor_to_list(bpu_escale),
        torch_tensor_to_list(
            bpu_escale_lshift))  # pylint: disable-msg=too-many-arguments

    return tm(hbir, tr.torch_native), dequant_output_scale


def max_pool2d(builder, annotated_name, node, input, kernel_size, stride,
               padding, dilation, ceil_mode, return_indices, march):
    assert isinstance(input, tm)
    tr = input.retrieve(torch_native=False)
    annotated_name = tr.process_name(annotated_name)
    assert return_indices == 0, "max_pool2d with return_indices true is not supported"
    hbir = hbir_base.CreateMaxPoolingLayer(
        tr.hbir, annotated_name, kernel_size, stride, padding, ceil_mode,
        tr.dtype(), annotated_name)
    return tm(hbir, tr.torch_native)


def avg_pool2d(builder, annotated_name, node, input, kernel_size, stride,
               padding, ceil_mode, count_include_pad, divisor_override, iscale,
               izero, idtype, oscale, ozero, dtype, march):
    assert isinstance(input, tm)
    assert ozero == 0
    assert izero == 0
    assert len(
        kernel_size
    ) == 2, annotated_name + "the lenth of the kernel_size list should equal to 2 "
    tr = input.retrieve(torch_native=False)
    annotated_name = tr.process_name(annotated_name)
    if builder.march_enum == March.BERNOULLI:
        tr.shift(iscale)
        assert iscale == oscale, "input and output scales must be identical for bernoulli"
        hbir = hbir_base.CreateAvgPoolingLayer(tr.hbir, annotated_name,
                                               kernel_size, stride,
                                               padding, ceil_mode, False,
                                               tr.dtype(), annotated_name)
        ret = tm(hbir, False)
        ret.shift(oscale)
    else:
        assert len(tr.shape()), annotated_name + " "
        channel = tr.shape()[-1]
        qscale, post_rshift, pre_rshift = gen_rescale_param(
            iscale / kernel_size[0] / kernel_size[1], "int32", oscale,
            dtype[1:], builder.march_enum)
        hbir = hbir_base.CreateSAvgPoolingLayer(
            tr.hbir, annotated_name, kernel_size, stride, padding, ceil_mode,
            True, dtype[1:], annotated_name, [] if dtype == "qint32" else
            pre_rshift.astype(np.int32).tolist() * channel, [] if
            dtype == "qint32" else qscale.astype(np.int32).tolist() * channel,
            [] if dtype == "qint32" else
            post_rshift.astype(np.int32).tolist() * channel)

    ret = tm(hbir, False)

    if dtype == 'qint32':
        return ret, iscale * (1 / kernel_size[0] / kernel_size[1])
    return ret, oscale


def interpolate(builder, annotated_name, node, input, size, scale, mode,
                align_corners, recompute_scale_factor, input_scale, input_zp,
                input_dtype, march):
    assert isinstance(input, tm)
    tr = input.retrieve(torch_native=False)
    annotated_name = tr.process_name(annotated_name)

    assert align_corners in [False, None]

    if builder.march_enum in [March.BERNOULLI2, March.BERNOULLI]:
        precision_bit_num = (8, 8)
        legacy_mode = True
    else:
        precision_bit_num = (16, 16)
        legacy_mode = False

    if size == None:
        size = []

    if scale == None:
        scale = []
    else:
        assert recompute_scale_factor is True

    if mode == "bilinear":
        hbir = hbir_base.CreateRoiResizeLayer(
            tr.hbir, annotated_name, (0, 0, -1, -1), size, scale,
            precision_bit_num, mode, 'boundary', 'center', legacy_mode,
            tr.dtype(), annotated_name)
    elif mode == "nearest":
        if (builder.march_enum == March.BAYES
                or builder.march_enum == March.B25E
                or builder.march_enum == March.B253):
            hbir = hbir_base.CreateRoiResizeLayer(
                tr.hbir, annotated_name, (0, 0, -1, -1), size, scale,
                precision_bit_num, mode, 'boundary', 'center', legacy_mode,
                tr.dtype(), annotated_name)
        else:
            if size != []:
                assert len(
                    tr.shape()
                ) == 4, annotated_name + " shape of input tensor should at least 1"
                assert len(size) == 2
                scale = [size[0] / tr.shape()[-3], size[1] / tr.shape()[-2]]

            assert len(
                scale
            ) == 2, annotated_name + " shape of scale should equal to 2"
            h_frac = scale[0] - int(scale[0])
            w_frac = scale[1] - int(scale[1])
            if h_frac == 0 and w_frac == 0:
                hbir = hbir_base.CreateNearestUpsampleLayer(
                    tr.hbir, annotated_name,
                    [int(scale[0]), int(scale[1])], tr.dtype(), annotated_name)
            else:
                raise ValueError("unsupported nearest upsample")

    return tm(hbir, tr.torch_native)


def add(builder, annotated_name, node, x, y, xscale, yscale, xzero, yzero,
        xdtype, ydtype, oscale, ozero, odtype, march):
    assert march != March.BERNOULLI, "not supported by bernoulli"

    # align torch_native flags
    torch_native = get_common_torch_native([x, y])

    # process constant
    x, y = to_hbir_tensor([x, y], annotated_name, [xdtype, ydtype],
                          torch_native)
    x = x.retrieve(torch_native)
    y = y.retrieve(torch_native)
    annotated_name = x.process_name(annotated_name)

    assert xzero == 0
    assert yzero == 0
    assert ozero == 0
    assert len(
        x.shape()), annotated_name + " shape of input x should be at least 1"
    assert len(
        y.shape()), annotated_name + " shape of input y should be at least 1"

    channel = max(x.shape()[-1], y.shape()[-1])

    if builder.march_enum == March.BERNOULLI2:
        if torch.gt(xscale, yscale):
            a, b = y, x
            ascale, bscale = yscale, xscale
        else:
            a, b = x, y
            ascale, bscale = xscale, yscale
        add_scale = torch.max(ascale / 127, bscale / (1 << 25))
        a_qscale = np.clip(
            np.floor(ascale.numpy() / add_scale.numpy() + 0.5), -128,
            127).astype(np.int32)
        b_rescale = np.floor(bscale.numpy() / add_scale.numpy() + 0.5).astype(
            np.int32)
        m, e = np.frexp(b_rescale)
        b_qscale = int(max(min(m * (1 << min(15, e)), 32767), 0))
        b_lshift = int(max(0, e - 15))
        o_qscale, o_post_rshift, o_pre_rshift = gen_rescale_param(
            add_scale, "int32", oscale, odtype[1:], builder.march_enum)
        ret = hbir_base.CreateSElementwiseAddX2a(
            a.hbir, b.hbir, annotated_name, True, odtype[1:], annotated_name,
            o_qscale.tolist() * channel,
            o_pre_rshift.tolist() * channel,
            o_post_rshift.tolist() * channel,
            a_qscale.tolist() * channel, [b_qscale] * channel,
            [b_lshift] * channel)
        return tm(ret, x.torch_native)

    # march bayes
    if torch.gt(xscale, yscale):
        a, b = x, y
        ascale, bscale = xscale, yscale
        adtype, bdtype = xdtype, ydtype
    else:
        a, b = y, x
        ascale, bscale = yscale, xscale
        adtype, bdtype = ydtype, xdtype
    shift0 = 23 if adtype == 'qint8' else 15
    shift1 = int(torch.floor(torch.log2(32767 * ascale / bscale)))
    shift = min(shift0, shift1)
    add_scale = ascale / (2**shift)
    b_qscale = int(
        torch.floor(bscale * (2**shift) / ascale + 0.5).clip(-32767, 32767))
    b_lshift = 0

    o_qscale, o_post_rshift, o_pre_rshift = gen_rescale_param(
        add_scale, "int32", oscale, odtype[1:], builder.march_enum)

    ret = hbir_base.CreateSElementwiseAdd(
        a.hbir, b.hbir, annotated_name, True, odtype[1:], annotated_name,
        o_qscale.tolist() * channel,
        o_pre_rshift.tolist() * channel,
        o_post_rshift.tolist() * channel, [shift] * channel,
        [b_qscale] * channel, [b_lshift] * channel)
    return tm(ret, x.torch_native)


def sub(builder, annotated_name, node, x, y, xscale, xzero, xdtype, yscale,
        yzero, ydtype, oscale, ozero, odtype, march):
    assert march not in [March.BERNOULLI, March.BERNOULLI2
                         ], "not supported by bernoulli and bernoulli2"
    torch_native = get_common_torch_native([x, y])

    # process constant
    x, y = to_hbir_tensor([x, y], annotated_name, [xdtype, ydtype],
                          torch_native)
    x = x.retrieve(torch_native)
    y = y.retrieve(torch_native)
    annotated_name = x.process_name(annotated_name)

    assert xzero == 0
    assert yzero == 0
    assert ozero == 0

    channel = max(x.shape()[-1], y.shape()[-1])

    if torch.ge(xscale, yscale):
        a, b = x, y
        ascale, bscale = xscale, yscale
        adtype, bdtype = xdtype, ydtype
        negative_inter_scale = 1
    else:
        a, b = y, x
        ascale, bscale = yscale, xscale
        adtype, bdtype = ydtype, xdtype
        negative_inter_scale = -1
    shift0 = 23 if adtype == 'qint8' else 15
    shift1 = int(torch.floor(torch.log2(32767 * ascale / bscale)))
    shift = min(shift0, shift1)
    add_scale = ascale / (2**shift)

    b_qscale = int(
        torch.floor(-bscale * (2**shift) / ascale + 0.5).clip(-32767, 32767))
    b_lshift = 0

    o_qscale, o_post_rshift, o_pre_rshift = gen_rescale_param(
        negative_inter_scale * add_scale, "int32", oscale, odtype[1:],
        builder.march_enum)

    ret = hbir_base.CreateSElementwiseAdd(
        a.hbir, b.hbir, annotated_name, True, odtype[1:], annotated_name,
        o_qscale.tolist() * channel,
        o_pre_rshift.tolist() * channel,
        o_post_rshift.tolist() * channel, [shift] * channel,
        [b_qscale] * channel, [b_lshift] * channel)
    return tm(ret, x.torch_native)


def channel_shuffle(builder, annotated_name, node, input, groups):
    tr = input.retrieve(torch_native=False)
    assert len(tr.shape(
    )), annotated_name + " shape of input tensor should be at least 1"
    annotated_name = tr.process_name(annotated_name)

    channel = tr.shape()[-1]
    assert channel % groups == 0, "Number of channels must be divisible by groups. Got " + str(
        channel) + " channels and " + str(groups) + " groups."
    shuffle_index = []
    group_number = channel // groups
    for i in range(channel):
        groups_inner_index = i // groups
        groups_outer_index = i % groups
        shuffle_index.append(groups_outer_index * (group_number) +
                             groups_inner_index)
    hbir = hbir_base.CreateChannelShuffle(tr.hbir, annotated_name,
                                          shuffle_index, annotated_name)
    return tm(hbir, tr.torch_native)


def point_pillars_scatter(builder, annotated_name, node, voxel_feature, coords,
                          output_shape):
    tr1 = voxel_feature.retrieve(torch_native=True)
    tr2 = coords.retrieve(torch_native=True)
    annotated_name = tr1.process_name(annotated_name)
    output_name = annotated_name
    if output_name.endswith("_torch_native"):
        output_name = output_name[:-len("_torch_native")]
    hbir = hbir_base.CreateScatterLayer(tr1.hbir, tr2.hbir, output_shape,
                                        annotated_name, output_name)

    return tm(hbir, False)


def point_pillars_preprocess(builder,
                             annotated_name,
                             node,
                             points,
                             pc_range,
                             voxel_size,
                             max_voxels,
                             max_points_per_voxel,
                             use_max,
                             norm_range=torch.tensor([]),
                             norm_dims=torch.tensor([0, 1, 2],
                                                    dtype=torch.int)):
    assert use_max, annotated_name + " only support use_max True"
    if norm_range.numel() == 0:
        norm_range = pc_range.clone()
    norm_range = torch_tensor_to_list(norm_range)
    norm_dims = torch_tensor_to_list(norm_dims)
    assert len(points), annotated_name + " the points list shouldn't be empty"
    tr = points[0].retrieve(torch_native=True)
    pc_range = torch_tensor_to_list(pc_range)
    voxel_size = torch_tensor_to_list(voxel_size)
    annotated_name = tr.process_name(annotated_name)
    voxels_name = annotated_name
    if voxels_name.endswith("_torch_native"):
        voxels_name = voxels_name[:-len("_torch_native")]
    coords_name = tr.process_name(voxels_name + "_coords")
    hbirs = hbir_base.CreateGatherLayer(
        tr.hbir, annotated_name, voxel_size, pc_range, max_points_per_voxel,
        max_voxels, voxels_name, coords_name, norm_range, norm_dims, use_max)
    assert len(
        hbirs) == 2, annotated_name + " the length of hbirs should equal to 2"
    return [tm(hbirs[0], False), tm(hbirs[1], True)]


def detection_post_process_v1(
        builder, annotated_name, node, data, anchor, exp_table, image_sizes,
        num_classes, input_shifts, exp_shift, box_filter_threshold,
        class_offsets, seed, use_clippings, nms_threshold, nms_margin,
        post_nms_top_k, use_stable_sort: Optional[bool], march):
    for d in data:
        assert isinstance(d, tm), "must be placeholder not constant"

    assert len(data) and data[0].retrieve(torch_native=False).shape(
    )[0] == 1, annotated_name + "unsupported model: detection_post_process_v1 operator does not support batch mode"

    sample = None
    torch_sample = [(None, None, None)]
    if builder.run_pred:
        ret_sample = hqf.detection_post_process_v1(
            [d.native_sample for d in data], anchor, exp_table, image_sizes,
            num_classes, input_shifts, exp_shift, box_filter_threshold,
            class_offsets, seed, use_clippings, nms_threshold, nms_margin,
            post_nms_top_k, use_stable_sort, march)
        arrays = []
        for i, r in enumerate(ret_sample):
            assert len(r) == 3
            tensor = torch.cat([r[0], r[1].unsqueeze(-1), r[2].unsqueeze(-1)],
                               -1).unsqueeze(0).unsqueeze(0).to(torch.int32)
            arrays.append(tensor.numpy())

            new_r0 = torch.ones(r[0].shape[0], 4, dtype=r[0].dtype) * -1
            new_r0[:r[0].shape[0]] = r[0]

            new_r1 = torch.ones(r[1].shape[0], dtype=r[1].dtype) * -1
            new_r1[:r[1].shape[0]] = r[1]

            new_r2 = torch.ones(r[2].shape[0], dtype=r[2].dtype) * -1
            new_r2[:r[2].shape[0]] = r[2]
            torch_sample[0] = new_r0, new_r1, new_r2

        from hbdk.operator.conversion import convert_to_hardware_layout
        converteds = convert_to_hardware_layout(
            node, arrays, builder.march_enum, 'proposal', {})
        assert converteds
        sample = torch.tensor(converteds[0])

    data = [d.retrieve(torch_native=False) for d in data]
    annotated_name = data[0].process_name(annotated_name)

    assert len(anchor) and isinstance(anchor[0], torch.Tensor), \
        annotated_name + " anchor shouldn't be empty, and anchor[0] should be a tensor"
    anchor_name = annotated_name + ":anchor"
    exp_table_name = annotated_name + ":exp_table"

    dpp_branch = len(data)

    assert len(image_sizes) and isinstance(
        image_sizes,
        torch.Tensor), annotated_name + "image_size cannot be dynamic"
    assert len(
        image_sizes[0]
    ) >= 2, annotated_name + " the length of image_sizes[0] should larger than 2"
    image_h = image_sizes[0][0].item()
    image_w = image_sizes[0][1].item()

    num_anchors = [int(a.size(1) / 4) for a in anchor]
    anchor_start_idx = [0]
    for per_branch_num_anchors in num_anchors:
        anchor_start_idx.append(anchor_start_idx[-1] + per_branch_num_anchors)
    anchor_start_idx = anchor_start_idx[:-1]
    block_sizes = []
    max_input_size = 144 * 4 * 2048
    for num_anchor in num_anchors:
        ## Compiler would pad allocation size of the anchor to 4-aligned
        ## due to hardware restriction
        per_anchor_alloc_size = np.ceil((4 + num_classes) / 4.0) * 4
        max_tile_area = np.floor(
            max_input_size /
            (np.ceil(per_anchor_alloc_size * num_anchor / 4) * 4))
        max_tile_w = np.ceil(np.floor(np.sqrt(max_tile_area)) / 8) * 8
        max_tile_h = np.floor(max_tile_area / max_tile_w)
        if (builder.march_enum in [March.BERNOULLI2, March.BERNOULLI
                                   ]) and use_stable_sort:
            max_tile_w = (2**np.floor(np.log2(max_tile_w).item())).astype(
                np.int32)
            max_tile_h = (2**np.floor(np.log2(max_tile_h).item())).astype(
                np.int32)
        block_sizes.append((max_tile_h, max_tile_w))
    stride_hw = []
    for per_branch_anchor in anchor:
        assert len(
            per_branch_anchor.shape
        ) == 4, annotated_name + " shape of per_branch_anchor should equal to 4"
        stride_hw.append((
            int((per_branch_anchor[0, 1, 1, 0] -
                 per_branch_anchor[0, 1, 0, 0]).item()),
            int((per_branch_anchor[0, 0, 0, 1] -
                 per_branch_anchor[0, 0, 0, 0]).item()),
        ))
    anchor_table = torch.cat([
        per_branch_anchor[0, :, 0, 0].flatten() for per_branch_anchor in anchor
    ]).reshape(-1, 4)
    assert len(
        anchor_table.shape
    ) == 2, annotated_name + " the shape of anchor_table should equal to 2"
    x1 = anchor_table[:, 0]
    y1 = anchor_table[:, 1]
    x2 = anchor_table[:, 2]
    y2 = anchor_table[:, 3]
    anchor_table = torch.stack(
        [y2 - y1, x2 - x1, (y1 + y2) / 2, (x1 + x2) / 2], dim=-1)

    shifted_anchor = torch.clip(
        torch.floor(anchor_table * 4 + 0.5), -1 << 31,
        (1 << 31) - 1).to(dtype=torch.int32)

    if builder.march_enum in [March.BERNOULLI, March.BERNOULLI2]:
        if use_stable_sort is None:
            stable_sort = False
        else:
            stable_sort = use_stable_sort
    else:
        assert (use_stable_sort is
                None) or use_stable_sort, "Bayes only support stable sort!"
        stable_sort = True

    data = [d.hbir for d in data]

    hbir = hbir_base.CreateDetectionPostProcessLayer(
        data, annotated_name, anchor_name, exp_table_name, "",
        torch_tensor_to_list(shifted_anchor), torch_tensor_to_list(exp_table),
        num_anchors, [num_classes] * dpp_branch, input_shifts,
        [int(block_size[0]) for block_size in block_sizes],
        [int(block_size[1]) for block_size in block_sizes], class_offsets,
        anchor_start_idx, [s[0] for s in stride_hw], [s[1] for s in stride_hw],
        use_clippings, True, stable_sort, image_h, image_w, exp_shift,
        box_filter_threshold, seed, nms_threshold, nms_margin, post_nms_top_k,
        annotated_name + "_torch_native")

    assert len(input_shifts) > 0
    if builder.march_enum in [March.BERNOULLI]:
        hbir_base.SetTensorShift(hbir, [2, 2, 2, 2, input_shifts[0], 0])
    else:
        hbir_base.SetTensorScale(
            hbir, [0.25, 0.25, 0.25, 0.25, 1 / 2**input_shifts[0], 1.0])

    ret0 = tm(hbir, torch_native=True, native_sample=torch_sample[0][0])

    ret1 = tm(
        hbir_base.CreateTensor(annotated_name + "_dummy1_torch_native",
                               ret0.records[0].shape(), 'int8', [], [], []),
        torch_native=True,
        native_sample=torch_sample[0][1])
    ret2 = tm(
        hbir_base.CreateTensor(annotated_name + "_dummy2_torch_native",
                               ret0.records[0].shape(), 'int8', [], [], []),
        torch_native=True,
        native_sample=torch_sample[0][2])

    builder.inhardware_pred_record[hbir + '_inhardwarelayout'] = [
        'int16', sample
    ]
    return [
        (ret0, ret1, ret2),
    ]


def rcnn_post_process(builder, annotated_name, node, bbox_data, bbox_score,
                      bbox_deltas, im_info, original_img_h, original_img_w,
                      nms_threshold, score_threshold, class_number, nms_top_n,
                      bbox_delta_mean, bbox_delta_std, march):
    '''
    * RCNN Post Process Layer
    *
    * input [bbox_tensor, bbox_score, bbox_deltas]
    * 1. bbox_tensor shape is [num_batch, num_bbox, 6], no shift, type is int32
    *    one bbox has 6 numbers [x1, y1, x2, y2, score, class_index]
    * 2. bbox_score shape is [num_batch * num_bbox, 1, 1, (num_class + 1)], no shift, type is float32
    * 3. bbox_deltas shape is [num_batch * num_bbox, 1, 1, (num_class + 1) * 4], no shift, type is float32
    * 4. im_info shape is [N, 1, 1, 2], no shift values, type is int32, can be nullptr
    *
    * output [output0, output1]
    * 1. output0 shape is [num_batch, nms_top_n, 6], no shift, type is int32
    *    one bbox has 6 numbers [x1, y1, x2, y2, score, class_index]
    * 2. output1 shape is [num_batch, nms_top_n, 6], no shift, type is float32
    *    one bbox has 6 numbers [x1, y1, x2, y2, score, class_index]
    '''

    assert (builder.march_enum == March.BAYES
            or builder.march_enum == March.B25E
            or builder.march_enum == March.B253)
    if isinstance(bbox_data, list):
        assert len(bbox_data) == 1
        bbox_data = bbox_data[0]

    bbox_data_tr = bbox_data.retrieve(torch_native=True)
    bbox_score_tr = bbox_score.retrieve(torch_native=False)
    bbox_deltas_tr = bbox_deltas.retrieve(torch_native=False)
    im_info_hbir = 'null'
    image_size_fixed = True
    if im_info is not None:
        im_info_hbir = im_info.retrieve(torch_native=True).hbir
        image_size_fixed = False

    bpu_sample = [None, None]
    torch_sample = [None, None]
    if builder.run_pred:
        bbox_data_sample = bbox_data.native_sample
        bbox_score_sample = hqf.dequantize(bbox_score.native_sample,
                                           torch.Tensor(bbox_score_tr.scale()),
                                           torch.Tensor([0]), 1, march)
        bbox_deltas_sample = hqf.dequantize(
            bbox_deltas.native_sample, torch.Tensor(bbox_deltas_tr.scale()),
            torch.Tensor([0]), 1, march)
        im_info_sample = None
        if im_info is not None:
            im_info_sample = im_info.native_sample

        ret_sample = hqf.rcnn_post_process(
            [bbox_data_sample], bbox_score_sample, bbox_deltas_sample,
            im_info_sample, original_img_h, original_img_w, nms_threshold,
            score_threshold, class_number, nms_top_n, bbox_delta_mean,
            bbox_delta_std, march)
        torch_sample = ret_sample
        from hbdk.operator.conversion import convert_to_hardware_layout
        converteds = convert_to_hardware_layout(
            node, [t.numpy() for t in ret_sample], builder.march_enum,
            'proposal', {})
        assert converteds
        bpu_sample = [torch.Tensor(a) for a in converteds]

    annotated_name = bbox_data_tr.process_name(annotated_name)
    annotated_out0 = bbox_data_tr.process_name(annotated_name + "_int")
    annotated_out1 = bbox_data_tr.process_name(annotated_name + "_float")

    hbirs = hbir_base.CreateRcnnPostPorcessLayer(
        annotated_name, bbox_data_tr.hbir, bbox_score_tr.hbir,
        bbox_deltas_tr.hbir, im_info_hbir, original_img_h, original_img_w,
        nms_threshold, class_number, nms_top_n, score_threshold,
        bbox_delta_mean, bbox_delta_std, image_size_fixed, annotated_out0,
        annotated_out1)
    assert len(hbirs) == 2

    builder.inhardware_pred_record[hbirs[0] + '_inhardwarelayout'] = [
        'int16', bpu_sample[0]
    ]
    builder.inhardware_pred_record[hbirs[1] + '_inhardwarelayout'] = [
        'float', bpu_sample[1]
    ]
    return [
        tm(hbirs[0], True, native_sample=torch_sample[0]),
        tm(hbirs[1], True, native_sample=torch_sample[1])
    ]


def multi_scale_roi_align(
        builder, annotated_name, node, features, boxes, output_size,
        spatial_scale, sampling_ratio, aligned, interpolate_mode,
        canonical_box_size, canonical_level,
        box_clip_ratio: Optional[Tuple[float, float, float, float]], march):
    assert sampling_ratio == 1, "only support sampling_ratio = 1"
    assert interpolate_mode == "bilinear", "only support 'bilinear' mode now"

    if not isinstance(features, list):
        features = [features]
    if not isinstance(boxes, list):
        boxes = [boxes]

    for f in features:
        assert isinstance(f, tm), "must be placeholder but not constant"
    for b in boxes:
        assert isinstance(b, tm), "box must be placeholder not constant"

    features = [f.retrieve(torch_native=False) for f in features]
    boxes = [b.retrieve(torch_native=True) for b in boxes]
    assert len(boxes) == 1, "only support batch size == 1"

    annotated_name = features[0].process_name(annotated_name)
    is_fpn = False
    if boxes[0].dtype() == "float32":
        is_fpn = True
        assert builder.march_enum not in [March.BERNOULLI2, March.BERNOULLI]

    levels = (-torch.log2(torch.tensor(spatial_scale))).to(torch.int32)
    middle_layer_id = canonical_level - levels[0]

    def convert_spatial_scale(spatial_scale):
        spatial_scale_int = []
        for ss in spatial_scale:
            spatial_scale_int.append(int(1.0 / ss))
        return spatial_scale_int

    spatial_scale = convert_spatial_scale(spatial_scale)
    bbox_augment_param = [1, 0, 0, 0, 0]
    if is_fpn:
        # box scale in augmentation
        bbox_augment_param[2] = 1
        bbox_augment_param[3] = 1
    box_scale = False
    box_scale_ratio_param = []
    # import pdb
    # pdb.set_trace()
    if box_clip_ratio is not None:
        box_scale = True
        box_scale_ratio_param = list(box_clip_ratio)
    ret = hbir_base.CreateRoiAlignLayer(
        [f.hbir for f in features], annotated_name, boxes[0].hbir,
        output_size, spatial_scale, spatial_scale, canonical_box_size,
        middle_layer_id.item(), -128.0, 0, -1, 'avg', 'border', -1, False,
        False, bbox_augment_param, box_scale, box_scale_ratio_param, True,
        is_fpn, False, aligned, 16, True, 'int8', annotated_name)
    # pdb.set_trace()
    return tm(ret, torch_native=False)


def multi_table_fit(
        builder, annotated_name, node, data, data_scale, data_zero_point,
        data_type, dense_table, qint_dense_xmin, qint_dense_xmax, sparse_table,
        qint_sparse_xmin, qint_sparse_xmax, left_line_xmin, left_line_ymin,
        left_line_xmax, left_line_ymax, right_line_xmin, right_line_ymin,
        right_line_xmax, right_line_ymax, qint_left_constant_xmin,
        qint_left_constant_xmax, qint_right_constant_xmin,
        qint_right_constant_xmax, left_constant_fit_y, right_constant_fit_y,
        scale, zero_point, dtype, is_symmetric, symmetric_k, symmetric_b,
        march):
    assert builder.march_enum == March.BAYES1
    assert march == "bayes1"

    from horizon_plugin_pytorch.nn.quantized.functional import get_multi_table_params
    multi_table_params = get_multi_table_params(
        data_scale, data_zero_point, data_type, scale, zero_point, dtype,
        left_line_xmin, left_line_ymin, left_line_xmax, left_line_ymax,
        right_line_xmin, right_line_ymin, right_line_xmax, right_line_ymax,
        left_constant_fit_y, right_constant_fit_y, qint_dense_xmin,
        qint_dense_xmax, qint_sparse_xmin, qint_sparse_xmax, march)

    dense_params = multi_table_params["dense_table"]
    sparse_params = multi_table_params["sparse_table"]
    left_params = multi_table_params["left_line"]
    right_params = multi_table_params["right_line"]
    xmin_params = multi_table_params["left_constant"]
    xmax_params = multi_table_params["right_constant"]

    # (k, b, left_shift, right_shift)
    # (table, scale, bias, left_shift, p_shift, itplt_shift)  --- NOTE: right_shift = p_shift - itplt_shift
    def clip_value(x):
        return min(max(-2147483647, x), 2147483647)

    def get_attr_range(k, b, lsh, rsh, min, max):
        range = hbir_base.SLutAttrRange()
        range.k = k
        range.b = b
        range.lsh = lsh
        range.rsh = rsh
        range.min = min
        range.max = max
        range.neg_min = -1 * clip_value(min)  # avoid overflow
        range.neg_max = -1 * clip_value(max)
        range.neg_k = -1 * clip_value(k)
        return range

    def get_attr_table(table):
        table = torch_tensor_to_list(table)
        array = hbir_base.Int32Array256()
        for i, _ in enumerate(array):
            array[i] = int(table[i])
        return array

    attr = hbir_base.SLutAttr()
    assert len(
        attr.table_zone_ranges
    ) == 6, annotated_name + " length of table_zone_ranges list should equal to 6"
    assert len(
        dense_params
    ) == 6, annotated_name + " length of dense_params list should equal to 6"
    assert len(
        sparse_params
    ) == 6, annotated_name + " length of sparse_params list should equal to 6"
    assert len(
        left_params
    ) == 6, annotated_name + " length of left_params list should equal to 6"
    assert len(
        right_params
    ) == 6, annotated_name + " length of right_params list should euqal to 6"
    assert len(
        xmin_params
    ) >= 4, annotated_name + " length of xmin_params list should be at least 4"
    # range: dense, sparse, left, right, xmin, xmax
    attr.table_zone_ranges[0] = get_attr_range(
        dense_params[0], dense_params[2], dense_params[3],
        dense_params[4] - dense_params[5], qint_dense_xmin.item(),
        qint_dense_xmax.item())
    attr.table_zone_ranges[1] = get_attr_range(
        sparse_params[0], sparse_params[2], sparse_params[3],
        sparse_params[4] - sparse_params[5], qint_sparse_xmin.item(),
        qint_sparse_xmax.item())
    attr.table_zone_ranges[2] = get_attr_range(left_params[0], left_params[1],
                                               left_params[2], left_params[3],
                                               left_params[4], left_params[5])
    attr.table_zone_ranges[3] = get_attr_range(
        right_params[0], right_params[1], right_params[2], right_params[3],
        right_params[4], right_params[5])
    attr.table_zone_ranges[4] = get_attr_range(xmin_params[0], xmin_params[1],
                                               xmin_params[2], xmin_params[3],
                                               qint_left_constant_xmin.item(),
                                               qint_left_constant_xmax.item())
    attr.table_zone_ranges[5] = get_attr_range(xmax_params[0], xmax_params[1],
                                               xmax_params[2], xmax_params[3],
                                               qint_right_constant_xmin.item(),
                                               qint_right_constant_xmax.item())
    attr.symmetry_k = symmetric_k
    attr.symmetry_b = symmetric_b.item()
    attr.sparse_table = get_attr_table(sparse_table)
    attr.dense_table = get_attr_table(dense_table)
    if is_symmetric:
        attr.enable_symmetry = True
        attr.table_zone_ranges[5].neg_max = -32768
    else:
        attr.enable_symmetry = False
    attr.enable_rounding = True

    assert dtype in ['qint8', 'qint16']
    tr = data.retrieve()
    hbir = hbir_base.CreateSLutLayer(tr.hbir, annotated_name, annotated_name,
                                     dtype[1:], attr)

    return tm(hbir, tr.torch_native)


def segment_lut(builder, annotated_name, node, input, table, scales, beta,
                left_shift, right_shift, max, is_centrosymmetric, input_scale,
                input_zero_point, input_dtype, scale, zero_point, dtype,
                march):
    assert (builder.march_enum == March.BAYES
            or builder.march_enum == March.B25E
            or builder.march_enum == March.B253)
    assert input_dtype == "qint16"

    assert isinstance(input, tm)
    assert isinstance(table, torch.Tensor)
    assert isinstance(scales, torch.Tensor)
    assert isinstance(beta, torch.Tensor)
    assert isinstance(left_shift, torch.Tensor)
    assert isinstance(right_shift, torch.Tensor)
    assert isinstance(max, torch.Tensor)

    def get_attr_range(k, b, sum_rsh, add_lsh, max):
        range = hbir_base.Lut2AttrRange()
        range.k = k
        range.b = b
        range.sum_rsh = sum_rsh
        range.add_lsh = add_lsh
        range.max = max
        return range

    def get_attr_table(table):
        table = torch_tensor_to_list(table)
        array = hbir_base.Int16Array64()
        for i, _ in enumerate(array):
            array[i] = int(table[i])
        return array

    attr = hbir_base.Lut2Attr()
    assert len(
        attr.table_zone_ranges
    ) == 6, annotated_name + " length of table_zone_ranges should equal to 6"
    assert len(
        scales) == 8, annotated_name + " length of scales list should be 8"
    assert len(beta) == 8, annotated_name + " length of beta list should be 8"
    assert len(
        right_shift
    ) == 8, annotated_name + " length of right_shift list should be 8"
    assert len(
        left_shift
    ) == 8, annotated_name + " length of left_shift list should be 8"
    assert len(max) == 8, annotated_name + " length of max list should be 8"
    attr.left_line_range = get_attr_range(scales[0].item(), beta[0].item(),
                                          right_shift[0].item(),
                                          left_shift[0].item(), max[0].item())
    for i in range(6):
        attr.table_zone_ranges[i] = get_attr_range(
            scales[i + 1].item(), beta[i + 1].item(),
            right_shift[i + 1].item(), left_shift[i + 1].item(),
            max[i + 1].item())
        attr.tables[i] = get_attr_table(table[i])
    attr.right_line_range = get_attr_range(scales[7].item(), beta[7].item(),
                                           right_shift[7].item(),
                                           left_shift[7].item(), max[7].item())
    if is_centrosymmetric:
        attr.symmetry_mode = hbir_base.symmetry_mode_t_ORIGIN_SYMMETRIC
    attr.round_mode = hbir_base.round_mode_t_ROUND
    attr.enable_saturate = True

    tr = input.retrieve()
    annotated_name = tr.process_name(annotated_name)
    ret = hbir_base.CreateLut2([tr.hbir], annotated_name, annotated_name, attr,
                               dtype[1:])

    return tm(ret, tr.torch_native)


def lut(builder, annotated_name, node, data, data_scale, data_zero_point,
        data_type, table, scale, zero_point, dtype, march):
    tr = data.retrieve()
    annotated_name = tr.process_name(annotated_name)
    itype = tr.dtype()

    if itype == 'int8' and dtype == 'qint8':
        assert isinstance(table, torch.Tensor)

        table = torch_tensor_to_list(table)
        ret = hbir_base.CreateStepwiseFitLayer(
            tr.hbir, annotated_name, [], table, dtype[1:], annotated_name)
        return tm(ret, tr.torch_native)
    raise RuntimeError("unsupported lut")


def _set_annotation(builder, annotated_name, node, input, annotation):
    [hbir_base.SetAnnotation(r.hbir, annotation) for r in input.records]
    return input


def mul(builder, annotated_name, node, x, y, xscale, xzero, xdtype, yscale,
        yzero, ydtype, oscale, ozero, odtype, march):
    # align torch_native flags
    torch_native = get_common_torch_native([x, y])
    # process constant
    x, y = to_hbir_tensor([x, y], annotated_name, [xdtype, ydtype],
                          torch_native)

    x = x.retrieve(torch_native)
    y = y.retrieve(torch_native)
    annotated_name = x.process_name(annotated_name)

    assert len(x.shape()
               ), annotated_name + " the shape of input x should be at least 1"
    channel = x.shape()[-1]

    assert odtype != "qint32", "output type int32 not supported"
    o_qscale, o_post_rshift, o_pre_rshift = gen_rescale_param(
        xscale * yscale, "int32", oscale, odtype[1:], builder.march_enum)
    ret = hbir_base.CreateSElementwiseMul(x.hbir, y.hbir, annotated_name, True,
                                          odtype[1:], annotated_name,
                                          o_qscale.tolist() * channel,
                                          o_pre_rshift.tolist() * channel,
                                          o_post_rshift.tolist() * channel)
    return tm(ret, x.torch_native)


def sum(builder, annotated_name, node, input, dim, keepdim, x_scale,
        x_zero_point, x_dtype, scale, zero_point, dtype, march):
    assert isinstance(input, tm)
    tr = input.retrieve()
    dim = tr.transpose_dim(dim)
    annotated_name = tr.process_name(annotated_name)

    assert keepdim, "keepdim must be True!"

    qscale, post_rshift, pre_rshift = gen_rescale_param(
        x_scale, 'int32', scale, dtype[1:], builder.march_enum)

    hbir = hbir_base.CreateSSumLayer(tr.hbir, annotated_name, dtype[1:],
                                     annotated_name, dim, pre_rshift.tolist(),
                                     qscale.tolist(), post_rshift.tolist())
    return tm(hbir, tr.torch_native)


def mean(builder, annotated_name, node, input, dim, iscale, izero, idtype,
         oscale, ozero, odtype, march):
    assert isinstance(input, tm)
    tr = input.retrieve()
    dim = tr.transpose_dim(dim)
    annotated_name = tr.process_name(annotated_name)

    qscale, post_rshift, pre_rshift = gen_rescale_param(
        iscale, 'int32',
        oscale * tr.shape()[dim], odtype[1:], builder.march_enum)

    hbir = hbir_base.CreateSSumLayer(tr.hbir, annotated_name, odtype[1:],
                                     annotated_name, dim, pre_rshift.tolist(),
                                     qscale.tolist(), post_rshift.tolist())
    return tm(hbir, tr.torch_native)


def prelu(builder, annotated_name, node, input, weight, input_scale,
          input_zero_point, input_dtype, weight_scale, weight_zero_point,
          weight_dtype, scale, zero_point, dtype, march):
    weight = weight.reshape([1, -1, 1, 1])
    torch_native = get_common_torch_native([input, weight])
    input, weight = to_hbir_tensor([input, weight], annotated_name,
                                   [input_dtype, weight_dtype], torch_native)
    input = input.retrieve(torch_native)
    weight = weight.retrieve(torch_native)
    annotated_name = input.process_name(annotated_name)

    dtype = dtype[1:]
    p_qscale, p_post_rshift, p_pre_rshift = gen_rescale_param(
        input_scale, input_dtype[1:], scale, dtype, builder.march_enum)
    assert p_pre_rshift == 0
    n_qscale, n_post_rshift, n_pre_rshift = gen_rescale_param(
        input_scale * weight_scale, 'int32', scale, dtype, builder.march_enum)

    hbir = hbir_base.CreatePReluLayer(
        input.hbir, annotated_name, dtype, annotated_name, weight.hbir,
        p_qscale.tolist(), p_post_rshift.tolist(), n_pre_rshift.tolist(),
        n_qscale.tolist(), n_post_rshift.tolist())
    return tm(hbir, input.torch_native)


def correlation(builder, annotated_name, node, x, y, kernel, maxd, stride1,
                stride2, pad, is_mul, xscale, xzero, xdtype, yscale, yzero,
                ydtype, iscale, oscale, ozero, odtype, march):
    torch_native = get_common_torch_native([x, y])
    x, y = to_hbir_tensor([x, y], annotated_name, [xdtype, ydtype],
                          torch_native)
    x = x.retrieve(False)
    y = y.retrieve(False)
    annotated_name = x.process_name(annotated_name)
    if (kernel == 1):
        inter_right_shift = 0
        iscale = xscale * yscale
    else:
        inter_right_shift = np.math.floor(
            np.math.log(iscale / (xscale * yscale), 2))
    assert len(x.shape(
    )), annotated_name + " the shape of the input x should be at least 1"
    channel = x.shape()[-1]
    sumelems = channel * kernel * kernel
    o_qscale, o_post_rshift, o_pre_rshift = gen_rescale_param(
        iscale / sumelems, "int32", oscale, odtype[1:], builder.march_enum)
    ret = hbir_base.CreateSCorrelationLayer(
        x.hbir, y.hbir, annotated_name, kernel, maxd, stride1, stride2, pad,
        is_mul, odtype[1:], annotated_name, inter_right_shift,
        o_pre_rshift.tolist() * channel,
        o_qscale.tolist() * channel,
        o_post_rshift.tolist() * channel)
    return tm(ret, x.torch_native)


def pad(builder, annotated_name, node, input, pad, mode, value, scale,
        zero_point, dtype, march):
    assert isinstance(input, tm)
    if pad == [0] * len(pad):
        return input

    tr = input.retrieve()
    annotated_name = tr.process_name(annotated_name)

    pad_rank = len(pad) // 2
    unpad_rank = tr.rank() - pad_rank
    unpad_values = [0] * unpad_rank
    start = [*unpad_values, *pad[0::2][::-1]]
    end = [*unpad_values, *pad[1::2][::-1]]
    if not tr.torch_native and tr.rank() > 2:
        # NCHW -> NHWC
        start = start[:-3] + start[-2:] + start[-3:-2]
        end = end[:-3] + end[-2:] + end[-3:-2]
    if mode == 'circular':
        result = tr.hbir
        for r in range(-2, -2 - pad_rank, -1):
            to_be_concat = []
            result_shape = list(hbir_base.GetTensorShape(result))
            pad_before_begin = [0] * tr.rank()
            pad_before_begin[r] = -pad[(-r - 2) * 2]
            if pad_before_begin[r] != 0:
                pad_before = hbir_base.CreateSliceLayer(
                    result, annotated_name + "_slice_before" + str(r),
                    pad_before_begin, result_shape, [1, 1, 1, 1], dtype[1:],
                    annotated_name + "_slice_before" + str(r))
                to_be_concat.append(pad_before)
            to_be_concat.append(result)
            pad_after_end = result_shape
            pad_after_end[r] = pad[(-r - 2) * 2 + 1]
            if pad_after_end[r] != 0:
                pad_after = hbir_base.CreateSliceLayer(
                    result, annotated_name + "_slice_after" + str(r),
                    [0] * tr.rank(), pad_after_end, [1, 1, 1, 1], dtype[1:],
                    annotated_name + "_slice_after" + str(r))
                to_be_concat.append(pad_after)
            if len(to_be_concat) < 2:
                continue
            result = hbir_base.CreateConcatLayer(to_be_concat, annotated_name,
                                                 4 + r, tr.dtype(),
                                                 annotated_name + "_" + str(r))
        res = tm(result, tr.torch_native)
        return res

    if mode == 'constant':
        value = hqf.quantize(
            torch.tensor([value]), scale, zero_point, 0, dtype, march)
    mode_mp = {'constant': 'constant', 'replicate': 'edge'}
    assert mode in mode_mp.keys()
    hbir = hbir_base.CreatePadLayer(tr.hbir, annotated_name, mode_mp[mode],
                                    int(value), start, end, dtype[1:],
                                    annotated_name)
    return tm(hbir, tr.torch_native)


def filter(builder, annotated_name, node, inputs, scales, zeros, dtypes,
           thresh, idx_range, march):
    assert len(
        scales
    ), annotated_name + " the length of scales list shouldn't be empty"
    assert len(
        idx_range
    ) == 2, annotated_name + " the length of idx_range list should equal to 2"
    raw_ref = None
    is_bayes = (builder.march_enum == March.BAYES) or (
        builder.march_enum == March.B25E) or (builder.march_enum == March.B253)
    from .aten_registry import aten_cat

    cat_input = aten_cat(builder, annotated_name + "_pre_filter_cat", None,
                         inputs, 1)
    tr = cat_input.retrieve(torch_native=False)
    if builder.run_pred:
        # calculate reference
        for idx in range(tr.shape()[0]):
            sample = hqf.filter([i.native_sample for i in inputs], scales,
                                zeros, dtypes, thresh, idx_range, march)[idx]
            assert len(
                sample) >= 4, " the length of sample list should be at least 4"
            is_int16_data = True
            for dtype in dtypes:
                is_int16_data = is_int16_data and (dtype == "qint16")

            def decompose_int16(value):
                post_value = torch.Tensor(
                    (value.detach().numpy().astype(np.int16) & 0xff).astype(
                        np.int8)).unsqueeze(-1).to(torch.int8)
                pre_value = torch.Tensor(
                    (value.detach().numpy().astype(np.int16) >> 8).astype(
                        np.int8)).unsqueeze(-1).to(torch.int8)
                return torch.cat([post_value, pre_value], dim=-1)

            def decompose_int16_bayes(value):
                if is_int16_data:
                    return torch.Tensor((value.detach().numpy().astype(
                        np.int16))).unsqueeze(-1).to(torch.int16)
                else:
                    return decompose_int16(value)

            def decompose_float(value):  # handle sign bit extension
                pre_value = torch.Tensor(
                    ((value.detach().numpy() < 0) * -1)).unsqueeze(-1).to(
                        torch.float)
                return torch.cat([value.unsqueeze(-1), pre_value], dim=-1)

            def decompose_float_bayes(value):
                if is_int16_data:
                    return value.unsqueeze(-1).to(torch.float)
                else:
                    return decompose_float(value)

            if idx == 0:
                raw_ref = torch.cat([
                    decompose_int16_bayes(sample[1]).to(torch.float) if
                    is_bayes else decompose_int16(sample[1]).to(torch.float),
                    decompose_float_bayes(sample[0])
                    if is_bayes else decompose_float(sample[0]),
                    decompose_int16_bayes(sample[2][:, 0]).to(torch.float)
                    if is_bayes else decompose_int16(sample[2][:, 0]).to(
                        torch.float),
                    decompose_int16_bayes(sample[2][:, 1]).to(torch.float)
                    if is_bayes else decompose_int16(sample[2][:, 1]).to(
                        torch.float), *sample[3:]
                ],
                                    dim=-1)
            else:
                temp_raw_ref = torch.cat([
                    decompose_int16_bayes(sample[1]).to(torch.float) if
                    is_bayes else decompose_int16(sample[1]).to(torch.float),
                    decompose_float_bayes(sample[0])
                    if is_bayes else decompose_float(sample[0]),
                    decompose_int16_bayes(sample[2][:, 0]).to(torch.float)
                    if is_bayes else decompose_int16(sample[2][:, 0]).to(
                        torch.float),
                    decompose_int16_bayes(sample[2][:, 1]).to(torch.float)
                    if is_bayes else decompose_int16(sample[2][:, 1]).to(
                        torch.float), *sample[3:]
                ],
                                         dim=-1)
                raw_ref = torch.cat([raw_ref, temp_raw_ref])
        raw_ref = raw_ref.unsqueeze(0)
        raw_ref = raw_ref.unsqueeze(0)

    threshold_min = -32768
    threshold_max = 32767
    input_is_int8 = True
    for dtype in dtypes:
        if is_bayes:
            assert dtype == "qint8" or dtype == "qint16"
            if dtype == "qint8":
                threshold_min = -128
                threshold_max = 127
            else:
                assert threshold_min == -32768 and threshold_max == 32767
                input_is_int8 = False
                threshold_min = -32768
                threshold_max = 32767
        else:
            assert dtype == "qint8"
            threshold_min = -128
            threshold_max = 127

    annotated_name = tr.process_name(annotated_name)
    threshold_value = int(
        np.clip(
            np.floor(thresh / scales[0].numpy()), threshold_min,
            threshold_max))
    # please update threshold if data can not align plugin
    if is_bayes:
        threshold_value = int(
            np.clip(
                np.ceil(thresh / scales[0].numpy()), threshold_min,
                threshold_max))
    ret = hbir_base.CreateFilterLayer(
        [tr.hbir],
        annotated_name,
        1,
        threshold_value,
        0,
        idx_range[0],
        idx_range[1] - 1,  # endc inclusive
        "none",
        annotated_name + "_torch_native")

    def normalize_scale(scale, channel):
        return scale.numpy().tolist() * channel

    hbir_scales = [
        *normalize_scale(torch.ones(1), 2), *normalize_scale(scales[0], 1),
        *normalize_scale(torch.ones(1), 5)
    ]
    if not input_is_int8:
        hbir_scales = [
            *normalize_scale(torch.ones(1), 1), *normalize_scale(scales[0], 1),
            *normalize_scale(torch.ones(1), 2)
        ]

    for i, s in zip(inputs, scales):
        i_channel_number = i.retrieve(torch_native=False).shape()[-1]
        hbir_scales.extend(normalize_scale(s, i_channel_number))

    hbir_base.SetTensorScale(ret, hbir_scales)

    return [
        [tm(ret, torch_native=True, native_sample=raw_ref)] * (3 + len(inputs))
    ]


def cat(builder, annotated_name, node, inputs, dim, iscales, izeros, idtypes,
        oscale, ozero, odtype, march):
    torch_native = get_common_torch_native(
        inputs)  # align multiple TensorManagers
    tms = to_hbir_tensor(inputs, annotated_name, idtypes, torch_native)
    rescaled_inputs = []
    for idx, input, iscale, izero, idtype in zip(
            range(len(tms)), tms, iscales, izeros, idtypes):
        rescale_annotated_name = annotated_name + "_rescale_" + str(idx)
        # check if rescale already exists. in case cat multiple same tensors.
        if rescale_annotated_name in rescaled_inputs:
            rescaled_inputs.append(rescale_annotated_name)
        else:
            rescaled_inputs.append(
                requantize(builder, rescale_annotated_name, node, input,
                           iscale, izero, idtype, oscale, ozero, odtype, march,
                           torch_native))
        if builder.march_enum == March.BERNOULLI:
            input.shift(iscale)
            rescaled_inputs[-1].shift(oscale)
    from .aten_registry import aten_cat

    return aten_cat(builder, annotated_name, node, rescaled_inputs, dim)


def grid_sample(builder, annotated_name, node, input, grid, mode, padding_mode,
                align_corner, grid_scale, grid_zero, grid_dtype, march):
    tr = input.retrieve(torch_native=False)
    feat_n, feat_h, feat_w, feat_c = tr.shape()

    grid_n, grid_h, grid_w, grid_c = grid.size() if isinstance(
        grid, torch.Tensor) else grid.retrieve(torch_native=True).shape()
    grid_shift = int(
        np.clip(
            15 - np.ceil(
                np.log2(np.max([feat_h, feat_w, grid_h, grid_w]) + 1)), 0, 8))
    # grid_scale is scalar or vector, same for grid_out_scale
    grid_out_scale = torch.tensor([1.0 / (1 << grid_shift)],
                                  dtype=torch.float).reshape(grid_scale.shape)

    if isinstance(grid, torch.Tensor):
        grid = hqf.requantize(
            grid,
            grid_scale,
            grid_zero,
            grid_dtype,
            grid_out_scale,
            grid_zero,
            "qint16",
            march,
        )
        grid_scale = grid_out_scale
        grid_dtype = "qint16"
    grid = to_hbir_tensor([grid], annotated_name + "_grid", [grid_dtype],
                          True)[0]
    grid.shift(grid_out_scale)  # some shift logic left.

    grid = requantize(builder, annotated_name + "_grid_rescale", node, grid,
                      grid_scale, grid_zero, grid_dtype, grid_out_scale,
                      grid_zero, "qint16", march)
    grid = grid.retrieve(torch_native=True)
    grid.shift(grid_out_scale)

    if padding_mode == 'zeros':
        padding_mode = 'constant'
    if padding_mode == 'border':
        padding_mode = 'boundary'

    hbir = hbir_base.CreateWarpingLayer(
        [tr.hbir, grid.hbir], annotated_name, [1, 1], [0, 0], [1, 1], "fmap",
        False, False, False, 0, 0, True, mode, padding_mode, annotated_name)
    return tm(hbir, torch_native=False)


def matmul(builder, annotated_name, node, lhs, rhs, lhs_trans, rhs_trans,
           lhs_scale, lhs_zero, lhs_dtype, rhs_scale, rhs_zero, rhs_dtype,
           oscale, ozero, odtype, march):
    assert lhs_dtype == rhs_dtype, "lhs and rhs must have same dtype"
    if lhs_dtype == 'qint16':
        assert builder.march_enum not in [March.BERNOULLI, March.BERNOULLI2]

        # We need to consider two constraints:
        #  1. BPU input range is limited to [-32768, 32767 - 128]
        #  2. Avoid overflow of sum operation
        #     For [M, K] [K, N] matmul, there are K values to be sumed, and
        #     the result is of int32 type, so each value is limited to
        #     [INT32_MIN / K, INT32_MAX / K], input value is limited to
        #     [-sqrt(INT32_MAX / K), sqrt(INT32_MAX / K)] ~=
        #     [INT16_MIN * sqrt(2 / K), INT16_MAX * sqrt(2 / K)]
        #     Input type is int16, and the value range is multiplied with
        #     sqrt(2 / K), so the scale should multiply with sqrt(K / 2)
        k_dim_on_lhs = -2 if lhs_trans else -1
        if isinstance(lhs, torch.Tensor):
            assert len(lhs.size()) > k_dim_on_lhs, annotated_name +\
                                                   " length os lhs.size() should larger than k_dim_on_lhs"
            k = lhs.size()[k_dim_on_lhs]
        else:
            k = lhs.retrieve(torch_native=True).shape()[k_dim_on_lhs]
        rscale = max(32767 / (32767 - 128), np.math.sqrt(k / 2))

        lhs_dscale = lhs_scale * rscale
        # rhs_dscale = rhs_scale * rscale
        if isinstance(lhs, torch.Tensor):
            lhs = hqf.requantize(lhs, lhs_scale, lhs_zero, lhs_dtype,
                                 lhs_dscale, lhs_zero, lhs_dtype, march)
        else:
            lhs = requantize(builder, annotated_name + "_degrade_lhs", node,
                             lhs, lhs_scale, lhs_zero, lhs_dtype, lhs_dscale,
                             lhs_zero, lhs_dtype, march)
        lhs_scale = lhs_dscale

        rhs_dscale = rhs_scale * rscale
        if isinstance(rhs, torch.Tensor):
            rhs = hqf.requantize(rhs, rhs_scale, rhs_zero, rhs_dtype,
                                 rhs_dscale, rhs_zero, rhs_dtype, march)
        else:
            rhs = requantize(builder, annotated_name + "_degrade_rhs", node,
                             rhs, rhs_scale, rhs_zero, rhs_dtype, rhs_dscale,
                             rhs_zero, rhs_dtype, march)
        rhs_scale = rhs_dscale

    lhs, rhs = to_hbir_tensor([lhs, rhs], annotated_name,
                              [lhs_dtype, rhs_dtype], True)

    lhs = lhs.retrieve(torch_native=True)
    rhs = rhs.retrieve(torch_native=True)
    if builder.march_enum == March.BERNOULLI:
        lhs.shift(lhs_scale)
        rhs.shift(rhs_scale)

        hbir = hbir_base.CreateGemmLayer([lhs.hbir, rhs.hbir], annotated_name,
                                         1, 0, lhs_trans, rhs_trans, False,
                                         False, [0, 0, 0, 0], odtype[1:],
                                         annotated_name + "_torch_native")
        ret = tm(hbir, torch_native=True)
        ret.shift(oscale)
        return ret

    qscale, post_rshift, pre_rshift = gen_rescale_param(
        lhs_scale * rhs_scale, "int32", oscale, odtype[1:], builder.march_enum)
    assert len(rhs.shape(
    )) >= 2, annotated_name + " the length of rhs.shape should at least 2"
    channel = rhs.shape()[-2] if rhs_trans else rhs.shape()[-1]
    enableRounding = True
    if builder.march_enum in [March.BERNOULLI, March.BERNOULLI2]:
        enableRounding = False
    annotated_name = lhs.process_name(annotated_name)
    hbir = hbir_base.CreateSGemmLayer(
        [lhs.hbir, rhs.hbir], annotated_name, 1, 0, lhs_trans, rhs_trans,
        False, False, [0, 0, 0, 0], odtype[1:],
        qscale.astype(np.int32).tolist() * channel,
        pre_rshift.astype(np.int32).tolist() * channel,
        post_rshift.astype(np.int32).tolist() * channel, enableRounding,
        annotated_name + "_torch_native")

    return tm(hbir, torch_native=True)


def linear(builder, annotated_name, node, input, weight, bias, sumin,
           activation, input_scale, input_zero_point, input_dtype,
           weight_scale, weight_zero_point, weight_dtype, bias_scale,
           bias_zero_point, bias_dtype, sumin_scale, sumin_zero_point,
           sumin_dtype, scale, zero_point, dtype, march):
    assert (builder.march_enum == March.BAYES
            or builder.march_enum == March.B25E
            or builder.march_enum == March.B253)
    assert isinstance(input, tm)
    weight_dim4 = weight.reshape(list(weight.shape) + [1, 1])
    tr = input.retrieve(torch_native=True)
    annotated_name = tr.process_name(annotated_name)

    assert len(weight_dim4), annotated_name + " weight_dim4 shouldn't be empty"
    filters = weight_dim4.size()[0]
    weight_name = annotated_name + "_weight"
    bias_name = annotated_name + "_bias"

    from horizon_plugin_pytorch.nn.quantized.functional import conv2d_convert_int_params

    (bpu_weight, bpu_bias, bpu_bias_lshift, bpu_escale, bpu_escale_lshift,
     bpu_oscale, bpu_accu_rshift, bpu_output_rshift,
     dequant_output_scale) = conv2d_convert_int_params(
         input_scale, weight_dim4, weight_scale, weight_dtype, bias,
         bias_scale, bias_dtype, scale, dtype,
         sumin_scale if sumin is not None else None, False, 1, march)
    enable_rounding = True

    bpu_weight = torch.permute(
        bpu_weight, [0, 2, 3, 1])  # from cin,cout,kh,kw to cin,kh,kw,cout

    if dtype == 'qint32':
        bpu_accu_rshift = []
        bpu_oscale = []
        bpu_output_rshift = torch.zeros(filters, dtype=torch.int32)
    if sumin == None:
        bpu_escale = []
        bpu_escale_lshift = []
    else:
        sumin = sumin.retrieve(torch_native=True)

    hbir = hbir_base.CreateSLinear(
        tr.hbir, annotated_name, filters, True, activation == "relu",
        sumin.hbir if sumin is not None else "null", dtype[1:], annotated_name,
        weight_name, torch_tensor_to_list(bpu_weight), bias_name,
        torch_tensor_to_list(bpu_bias), enable_rounding,
        torch_tensor_to_list(bpu_accu_rshift),
        torch_tensor_to_list(bpu_bias_lshift),
        torch_tensor_to_list(bpu_oscale),
        torch_tensor_to_list(bpu_output_rshift),
        torch_tensor_to_list(bpu_escale),
        torch_tensor_to_list(
            bpu_escale_lshift))  # pylint: disable-msg=too-many-arguments
    return tm(hbir, tr.torch_native), dequant_output_scale


def window_partition(builder, annotated_name, node, input, window_size):
    tr = input.retrieve(torch_native=True)
    annotated_name = tr.process_name(annotated_name)
    input_n, input_h, input_w, input_c = tr.shape()
    assert input_h % window_size == 0, \
        "invalid window_partition window_size, which should be divisible by h size, h is " + str(input_h)
    assert input_w % window_size == 0, \
        "invalid window_partition window_size, which should be divisible by w size, w is " + str(input_w)

    output_n = input_n * (input_h // window_size) * (input_w // window_size)
    output_h = window_size
    output_w = window_size
    hbir = hbir_base.CreateReshapeLayer(
        tr.hbir, annotated_name, "window_partition",
        [output_n, output_h, output_w, input_c], 'int8', annotated_name,
        [2, 2])
    return tm(hbir, torch_native=True)


def window_reverse(builder, annotated_name, node, input, window_size, H, W):
    tr = input.retrieve(torch_native=True)
    annotated_name = tr.process_name(annotated_name)
    input_n, input_h, input_w, input_c = tr.shape()
    assert input_h == window_size, annotated_name + ": invalid h size, should be equal to window_size"
    assert input_w == window_size, annotated_name + ": invalid w size, should be equal to window_size"
    assert H % window_size == 0, \
        "invalid window_reverse window_size, which should be divisible by H size, H is " + str(H)
    assert W % window_size == 0, \
        "invalid window_reverse window_size, which should be divisible by W size, W is " + str(W)
    window_num = (H // window_size) * (W // window_size)
    assert input_n % window_num == 0, \
        "invalid input shape and window_size, input_n should be divisible by (H // window_size) * (W // window_size)"
    output_n = input_n // window_num
    hbir = hbir_base.CreateReshapeLayer(
        tr.hbir, annotated_name, "window_reverse", [output_n, H, W, input_c],
        'int8', annotated_name, [2, 2])
    return tm(hbir, torch_native=True)


def rle(builder, annotated_name, node, input, odtype):
    raw_ref = None
    if builder.run_pred:
        # calculate reference
        def rle_decompress(rle_out_tlist):
            decompressed_tlist = []
            for t in rle_out_tlist:
                npt = t.detach().numpy()
                assert len(
                    npt.shape) == 1, 'rle output is not list of 1-d tensor?'
                data_len = (npt.shape[0] - 1) // 2  # remove malformed pair num
                begin_pos = 1
                decomp_npt = []
                assert (data_len - 1) * 2 + 1 < len(npt), \
                    annotated_name + " the value of (data_len - 1 ) * 2 + 1 should less than the length of npt"
                for i in range(data_len):
                    val = npt[i * 2 + 1]
                    num = npt[i * 2 + 2]
                    decomp_npt.extend([val] * num)
                decompressed_tlist.append(torch.Tensor(decomp_npt))
            return torch.cat(decompressed_tlist, dim=-1)

        samples = hf.rle(input.native_sample, get_torch_dtype(odtype))
        raw_ref = rle_decompress(samples)

    tr = input.retrieve()
    assert len(tr.shape()
               ), annotated_name + " the shape of the input should at least 1"
    annotated_name = tr.process_name(annotated_name)
    ret = hbir_base.CreateRleLayer(tr.hbir, annotated_name, tr.dtype(),
                                   annotated_name + "_torch_native")
    return [tm(ret, torch_native=True, native_sample=raw_ref)] * tr.shape()[0]


def topk(builder,
         annotated_name,
         node,
         input,
         k,
         dim=0,
         largest=True,
         is_sorted=True,
         index=True):
    tr = input.retrieve(torch_native=True)
    annotated_name = tr.process_name(annotated_name)
    input_shape = tr.shape()
    dim = (dim + len(input_shape)) % len(input_shape)

    tr_hbirs = hbir_base.CreateTopKElementsLayer(tr.hbir, annotated_name, k,
                                                 dim, largest, is_sorted, True,
                                                 "int32", annotated_name)
    return [tm(ir, tr.torch_native) for ir in tr_hbirs]


def abs(builder, annotated_name, node, input, overflow_mode):
    tr = input.retrieve()
    annotated_name = tr.process_name(annotated_name)
    if overflow_mode == "saturate":
        saturated_output = True
    elif overflow_mode == "trunc":
        saturated_output = False
    else:
        raise "unknown abs output overflow mode %s, only support 'saturate' or 'trunc'" % overflow_mode
    hbir = hbir_base.CreateElementwiseAbs(tr.hbir, annotated_name,
                                          saturated_output, annotated_name)
    return tm(hbir, tr.torch_native)


def ceil(builder, annotated_name, node, input, input_scale, input_zero_point,
         input_dtype, scale, zero_point, dtype, march):
    left_shift_scale = 1
    min_value = -32768
    max_value = 32767

    if input_dtype == "qint8":
        min_value = -128
        max_value = 127
    elif input_dtype == "qint16":
        min_value = -32768
        max_value = 32767
    else:
        assert "non support input data type"

    tr = input.retrieve(torch_native=False)

    m, e = np.frexp(input_scale)

    data_size = 1
    for item in tr.shape():
        data_size = data_size * item

    # 0.5 <= m < 1, so out_scale_int16 < 2 ^ left_shift_scale
    out_scale_int16 = int((m * (1 << left_shift_scale)).clamp(
        min_value, max_value).tolist()[0])

    out_right_shift = int((left_shift_scale - e).clamp(0, 30))

    # add_value = [int((np.power(2, left_shift_scale - e) - 1).clamp(min_value, max_value))] * data_size
    add_value = int(np.power(2, out_right_shift) - 1)

    input_zeros_tensor = hbir_base.CreateTensor(
        annotated_name + "_input_zeros", tr.shape(), "int8", [0] * data_size,
        [], [])

    input_scale_tensor = hbir_base.CreateTensor(
        annotated_name + "_input_scale", tr.shape(), input_dtype[1:],
        [out_scale_int16] * data_size, [], [])
    input_add_tensor = hbir_base.CreateTensor(annotated_name + "_input_add",
                                              tr.shape(), input_dtype[1:],
                                              [add_value] * data_size, [], [])
    output_right_shift_tensor = hbir_base.CreateTensor(
        annotated_name + "_output_right_shift", tr.shape(), "int8",
        [out_right_shift] * data_size, [], [])

    # so that out + 2 ** out_right_shift - 1 < 2 ^ 30 + 2 ^ 30 - 1 = 2 ^ 31 - 1
    # will not overflow int32
    # out = (out + np.power(2, out_right_shift) - 1).__rshift__(out_right_shift)
    hbir = hbir_base.CreateElementwiseAdd(
        input.retrieve().hbir, input_add_tensor, input_scale_tensor,
        input_zeros_tensor, output_right_shift_tensor, annotated_name, False,
        dtype[1:], annotated_name)
    return requantize(
        builder,
        "requantize_ceil_",
        node,
        tm(hbir, torch_native=False),
        torch.ones_like(input_scale),
        torch.zeros_like(input_scale).to(torch.long),
        dtype,
        scale,
        zero_point,
        dtype,
        march,
        torch_native=False)


def floor(builder, annotated_name, node, input, input_scale, input_zero_point,
          input_dtype, scale, zero_point, dtype, march):

    return requantize(builder, annotated_name + "re_requantize_floor_", node,
                      input, input_scale, input_zero_point, input_dtype, scale,
                      zero_point, dtype, march, False, False)


def softmax_bernoulli2(builder,
                       annotated_name,
                       node,
                       input,
                       table,
                       max_value_only=False,
                       dim=None,
                       march="bernoulli2"):
    '''
    softmax for x2a, migrated from mxnet 'SoftmaxOutput'
    :param builder:
    :param annotated_name:
    :param node:
    :param input:
    :param table: 256 elements with type uint8, for exp by look up table
    :param max_value_only:
    :param dim: Only support channel (1 for NCHW, 3 for NHWC)
    :return:
    '''
    assert isinstance(input, tm)
    tr = input.retrieve()
    if dim is None:
        dim = 3
    else:
        dim = tr.transpose_dim(dim)
    assert dim == 3, "only support dim is channel"

    annotated_name = tr.process_name(annotated_name)

    hbir = hbir_base.CreateSoftmaxX2X2A(tr.hbir, annotated_name,
                                        annotated_name,
                                        torch_tensor_to_list(table),
                                        max_value_only)
    return tm(hbir, tr.torch_native)
