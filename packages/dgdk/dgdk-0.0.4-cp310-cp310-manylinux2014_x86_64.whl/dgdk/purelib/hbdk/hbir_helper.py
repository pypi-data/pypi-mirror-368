import random
import sys
if sys.version_info >= (3, 10):
    from collections.abc import Iterable
else:
    from collections import Iterable

import numpy as np
from hbdk import hbir_base

random.seed(0)  # Use fixed seed to get reproducable param.
np.random.seed(0)
layer_idx = 0
tensor_idx = 0

int4 = "int4"
uint4 = "uint4"
int8 = "int8"
uint8 = "uint8"
int16 = "int16"
uint16 = "uint16"
int32 = "int32"
uint32 = "uint32"
float32 = "float32"


def SetSQuantiScope(v):
    assert isinstance(v, bool)
    hbir_base.SetSQuantiScope(v)


def CreateRandomInput(shapes, binary_file_name, types=(int8,)):
    assert isinstance(shapes, Iterable)
    if not isinstance(shapes[0], Iterable):
        shapes = [shapes]

    i = 0
    for shape in shapes:
        dtype = np.dtype(types[0]) if len(types) == 1 else np.dtype(types[i])
        a = np.clip((np.random.normal(0, 0.2, shape) *
                     np.iinfo(dtype).max).astype(int32),
                    np.iinfo(dtype).min,
                    np.iinfo(dtype).max).astype(dtype)
        shape_str = str(shape[0]) + 'x' + str(shape[1]) + 'x' + str(
            shape[2]) + 'x' + str(shape[3])
        with open(
                binary_file_name + "_input" + str(i) + "_" + shape_str +
                ".bin", 'wb') as f:
            a.tofile(f)
        i += 1


def ReturnOrAssignName(name, prefix=''):
    global layer_idx
    if name == 'null':
        name = prefix + str(layer_idx)
        layer_idx += 1
        return name
    return name


class Model(hbir_base.Model):
    pass


def GetTensor(name: str):
    return hbir_base.Tensor(name)


def GetLayer(name: str):
    return hbir_base.Layer(name)


def CleanUpContext():
    hbir_base.CleanUpContext()


def ModelInput(shape, name='null', element_type=int8, shift=None, scale=None):
    global tensor_idx
    if name == 'null':
        name = 'input_' + str(tensor_idx)
        tensor_idx += 1
    if shift is None:
        shift = []
    if scale is None:
        scale = []
    return hbir_base.CreateTensor(name, shape, element_type, [], shift, scale)


def Tensor(shape, element_type=int8, data=(), shift=(), scale=(), name='null'):
    global tensor_idx
    if name == 'null':
        name = 'tensor_' + str(tensor_idx)
        tensor_idx += 1
    return hbir_base.CreateTensor(name, shape, element_type, data, shift,
                                  scale)


def QuantiInput(input_tensor, name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    name = ReturnOrAssignName(name, "quantiinput_")
    return hbir_base.CreateQuantiInputLayer(input_tensor, name, int8,
                                            name + "_output")


def Convolution(input_tensor,
                sumin='null',
                num_filter=1,
                kernel=(1, 1),
                stride=(1, 1),
                pad=(0, 0),
                dilation=(1, 1),
                num_group=1,
                use_bias=True,
                use_relu=False,
                output_type=int8,
                weight_type=int8,
                enable_rounding=False,
                name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    assert output_type in [int8, int16, int32]
    name = ReturnOrAssignName(name, 'conv_')
    return hbir_base.CreateConvolutionLayer(
        input_tensor, name, num_filter, kernel, stride, pad, dilation,
        num_group, use_bias, use_relu, sumin, output_type, name + "_output",
        weight_type, name + "_weight", [], name + "_bias", [], enable_rounding)  # pylint: disable=too-many-arguments


def Deconvolution(input_tensor,
                  sumin='null',
                  num_filter=1,
                  kernel=(1, 1),
                  stride=(1, 1),
                  pad=(0, 0),
                  output_pad=(0, 0),
                  num_group=1,
                  use_bias=True,
                  use_relu=False,
                  enable_rounding=False,
                  name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    name = ReturnOrAssignName(name, 'dconv_')
    return hbir_base.CreateDeconvolutionLayer(
        input_tensor, name, num_filter, kernel, stride, pad, output_pad,
        num_group, use_bias, use_relu, sumin, int8, name + "_output", int8,
        name + "_weight", [], name + "_bias", [], enable_rounding)


def Conv3d(input_tensor,
           sumin='null',
           num_filter=1,
           kernel=(1, 1, 1),
           stride=(1, 1, 1),
           pad=(0, 0, 0),
           dilation=(1, 1, 1),
           num_group=1,
           use_bias=True,
           use_relu=False,
           output_type=int8,
           accu_right_shift=None,
           bias_left_shift=None,
           output_scale=None,
           output_right_shift=None,
           sumin_scale=None,
           sumin_left_shift=None,
           enable_rounding=False,
           name='null'):
    if accu_right_shift is None:
        accu_right_shift = []
    if bias_left_shift is None:
        bias_left_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []
    if sumin_scale is None:
        sumin_scale = []
    if sumin_left_shift is None:
        sumin_left_shift = []
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    assert output_type in [int8, int16, int32]
    name = ReturnOrAssignName(name, 'conv3d_')
    return hbir_base.CreateConv3dLayer(
        input_tensor, name, kernel, stride, pad, dilation, num_filter,
        num_group, use_bias, use_relu, sumin, name + "_weight", [],
        name + "_bias", [], name + "_output", output_type, enable_rounding,
        bias_left_shift, output_scale, accu_right_shift, sumin_scale,
        sumin_left_shift, output_right_shift)


def Pooling(input_tensor,
            kernel=(2, 2),
            stride=(2, 2),
            pad=(0, 0),
            mode='max',
            ceil_mode=False,
            name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    assert mode in ['max', 'average']
    name = ReturnOrAssignName(name, "pool_" + mode + "_")
    if mode == 'max':
        return hbir_base.CreateMaxPoolingLayer(input_tensor, name, kernel,
                                               stride, pad, ceil_mode, int8,
                                               name + "_output")
    if mode == 'average':
        return hbir_base.CreateAvgPoolingLayer(input_tensor, name, kernel,
                                               stride, pad, ceil_mode, True,
                                               int8, name + "_output")
    sys.exit(-1)


def GlobalPooling(input_tensor,
                  mode='average',
                  name='null',
                  accu_right_shift=None,
                  output_scale=None,
                  output_right_shift=None,
                  enable_rounding=False):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    assert mode in ['max', 'average']
    name = ReturnOrAssignName(name, "gpool_" + mode + "_")
    if mode == 'max':
        return hbir_base.CreateGlobalMaxPoolingLayer(input_tensor, name, int8,
                                                     name + "_output")
    if accu_right_shift is None:
        accu_right_shift = []

    if output_scale is None:
        output_scale = []

    if output_right_shift is None:
        output_right_shift = []

    if mode == 'average':
        return hbir_base.CreateGlobalAvgPoolingLayer(  # pylint: disable-msg=too-many-function-args
            input_tensor, name, enable_rounding, int8, name + "_output",
            accu_right_shift, output_scale, output_right_shift)
    sys.exit(-1)


def RoiResize(input_tensor,
              roi=(0, 0, -1, -1),
              interp_mode='bilinear',
              pad_mode='boundary',
              align_mode='origin',
              scale_factor=None,
              target_shape=None,
              precision=8,
              legacy_mode=True,
              name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    if (scale_factor is not None) and (not isinstance(scale_factor, Iterable)):
        scale_factor = [scale_factor, scale_factor]

    if not isinstance(precision, Iterable):
        precision = [precision, precision]

    assert pad_mode in ['zero', 'boundary']
    assert align_mode in ['origin', 'center']
    name = ReturnOrAssignName(name, "resize_roi_")
    return hbir_base.CreateRoiResizeLayer(
        input_tensor, name, roi,
        target_shape if target_shape is not None else [],
        scale_factor if scale_factor is not None else [], precision,
        interp_mode, pad_mode, align_mode, legacy_mode, int8, name + "_output")


def ScaleRelu(input_tensor, scales, shifts, name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
    name = ReturnOrAssignName(name, "scalerelu_")
    return hbir_base.CreateScaleReluLayer(input_tensor, name, scales, shifts,
                                          int8, name + "_output")


def LeakyRelu(input_tensor, negative_slop, name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    if not isinstance(negative_slop, Iterable):
        negative_slop = [negative_slop]
    name = ReturnOrAssignName(name, "scalerelu_")
    return hbir_base.CreateLeakyReluLayer(input_tensor, name, negative_slop,
                                          int8, name + "_output")


def PRelu(input_tensor,
          weight_tensor,
          output_type,
          positive_scale,
          positive_right_shift,
          accu_right_shift,
          negative_scale,
          negative_right_shift,
          name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, "prelu_")
    return hbir_base.CreateSPReluLayer(
        input_tensor, name, output_type, name + "_output", weight_tensor,
        positive_scale, positive_right_shift, accu_right_shift, negative_scale,
        negative_right_shift)


def Split(input_tensor, dim, split_num, splits=(), name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, "split_")
    return hbir_base.CreateSplitLayer(input_tensor, name, dim, split_num,
                                      splits, int8, name + "_output")


def Concat(input_tensors, dim=3, name='null'):
    assert isinstance(input_tensors, Iterable)
    name = ReturnOrAssignName(name, "concat_dim" + str(dim) + "_")
    return hbir_base.CreateConcatLayer(input_tensors, name, dim, int8,
                                       name + "_output")


def ChannelSum(input_tensor, name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, "channelsum_")
    return hbir_base.CreateChannelSumLayer(input_tensor, name, int8,
                                           name + "_output")


def SSum(input_tensor,
         dim,
         output_type=int8,
         accu_right_shift=None,
         output_scale=None,
         output_right_shift=None,
         name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, "ssum_")
    if accu_right_shift is None:
        accu_right_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []
    return hbir_base.CreateSSumLayer(input_tensor, name, output_type,
                                     name + "_output", dim, accu_right_shift,
                                     output_scale, output_right_shift)


def Filter(input_tensor,
           anchor_num,
           threshold,
           max_box_num,
           start_channel,
           end_channel,
           post_process='none',
           name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1 or len(input_tensor) == 2
    name = ReturnOrAssignName(name, "filter_")
    return hbir_base.CreateFilterLayer(
        input_tensor, name, anchor_num, threshold, max_box_num, start_channel,
        end_channel, post_process, name + "_output")


def RoiAlign(input_tensors,
             bbox_tensor,
             roi_output_shape,
             feature_stride_h,
             feature_stride_w,
             base_image_scale=224,
             middle_layer_id=0,
             ignore_score_value=-128.0,
             num_pooling=-1,
             max_num_pooling=-1,
             pool_method='avg',
             padding_mode='shrink',
             area_index=-1,
             clip_box=False,
             box_augmentation=False,
             box_augmentation_params=(),
             legacy_roi=True,
             is_fpn_roiresize=False,
             light_inter_linear=False,
             aligned=True,
             step_shift=0,
             correct_roi=False,
             use_box_scale=False,
             box_scale_params=(),
             name='null'):
    assert isinstance(input_tensors, Iterable)
    name = ReturnOrAssignName(name, 'roialign_')
    assert pool_method in ['avg', 'max']
    assert padding_mode in ['shrink', 'zero', 'nearest', 'border']
    return hbir_base.CreateRoiAlignLayer(
        input_tensors, name, bbox_tensor, roi_output_shape, feature_stride_h,
        feature_stride_w, base_image_scale, middle_layer_id,
        ignore_score_value, num_pooling, max_num_pooling, pool_method,
        padding_mode, area_index, clip_box, box_augmentation,
        box_augmentation_params, use_box_scale, box_scale_params, legacy_roi,
        is_fpn_roiresize, light_inter_linear, aligned, step_shift, correct_roi,
        int8, name + "_output")


def LinearPolynomial(input_tensor,
                     precision=8,
                     output_channel_num=1,
                     per_channel_mode=False,
                     name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    name = ReturnOrAssignName(name, 'linearpoly_')
    return hbir_base.CreateLinearPolynomialLayer(
        input_tensor, name, precision, output_channel_num, per_channel_mode)


def Relu(input_tensor, name='null', output_type=int8):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    name = ReturnOrAssignName(name, "relu_")
    return hbir_base.CreateReluLayer(input_tensor, name, output_type,
                                     name + "_output")


def OpticalPyramid(input_tensor,
                   pyramid_level,
                   scalar_outputs,
                   grad_outputs,
                   padding_pixel,
                   border_mode='BORDER_REFLECT_101',
                   scalar_element_type='uint8',
                   gradient_element_type="int8",
                   input_mode='FOLD_W_TO_C_4',
                   name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    name = ReturnOrAssignName(name, 'optical_pyramid_')
    return hbir_base.CreateOpticalPyramidLayer(
        input_tensor, name, pyramid_level, scalar_outputs, grad_outputs,
        padding_pixel, border_mode, scalar_element_type, gradient_element_type,
        input_mode)


def ConvertBetweenInt8AndUint8(inputs, name='null'):
    if not isinstance(inputs, list):
        inputs = [inputs]
    assert len(inputs) == 1
    name = ReturnOrAssignName(name, "convert_between_int8_and_uint8_")
    return hbir_base.CreateConvertBetweenInt8AndUint8Layer(
        inputs[0], name, int8, name + "_output")


def Slice(input_tensor, begin, end, step=(1, 1, 1, 1), name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, "slice_")

    return hbir_base.CreateSliceLayer(input_tensor, name, begin, end, step,
                                      int8, name + "_output")


def Pad(input_tensor,
        mode,
        pad_before,
        pad_after,
        constant_value=0,
        name='null'):
    '''
    Create pad layer
    :param input_tensors:
    :param mode: 'constant','edge'
    :param pad_before: pad before of each dim
    :param pad_after: pad after of each dim
    :param constant_value: default is 0
    :param name: layer name
    :return:
    '''
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    assert mode in ['zero', 'constant', 'edge']
    name = ReturnOrAssignName(name, 'pad_')
    return hbir_base.CreatePadLayer(input_tensor, name, mode, constant_value,
                                    pad_before, pad_after, int8,
                                    name + "_output")


def Correlation(input_tensor1,
                input_tensor2,
                kernel_size=1,
                max_displacement=1,
                stride1=1,
                stride2=1,
                pad_size=0,
                is_multiply=True,
                name='null'):
    if isinstance(input_tensor1,
                  Iterable) and not isinstance(input_tensor1, (str, bytes)):
        assert len(input_tensor1) == 1
        input_tensor1 = input_tensor1[0]

    if isinstance(input_tensor2,
                  Iterable) and not isinstance(input_tensor2, (str, bytes)):
        assert len(input_tensor2) == 1
        input_tensor2 = input_tensor2[0]

    name = ReturnOrAssignName(name, 'correlation_')
    return hbir_base.CreateCorrelationLayer(
        input_tensor1, input_tensor2, name, kernel_size, max_displacement,
        stride1, stride2, pad_size, is_multiply, int8, name + "_output")


def SCorrelation(input_tensor1,
                 input_tensor2,
                 kernel_size=1,
                 max_displacement=1,
                 stride1=1,
                 stride2=1,
                 pad_size=0,
                 is_multiply=True,
                 inter_right_shift=0,
                 accu_right_shift=None,
                 output_scale=None,
                 output_right_shift=None,
                 name='null'):
    if isinstance(input_tensor1,
                  Iterable) and not isinstance(input_tensor1, (str, bytes)):
        assert len(input_tensor1) == 1
        input_tensor1 = input_tensor1[0]
    if isinstance(input_tensor2,
                  Iterable) and not isinstance(input_tensor2, (str, bytes)):
        assert len(input_tensor2) == 1
        input_tensor2 = input_tensor2[0]
    if accu_right_shift is None:
        accu_right_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []

    name = ReturnOrAssignName(name, 'scorrelation_')
    return hbir_base.CreateSCorrelationLayer(
        input_tensor1, input_tensor2, name, kernel_size, max_displacement,
        stride1, stride2, pad_size, is_multiply, int8, name + '_output',
        inter_right_shift, accu_right_shift, output_scale, output_right_shift)


def ElementwiseMul(input_tensor1,
                   input_tensor2,
                   enable_rounding=False,
                   high_precision_output=False,
                   name='null'):
    if isinstance(input_tensor1,
                  Iterable) and not isinstance(input_tensor1, (str, bytes)):
        assert len(input_tensor1) == 1
        input_tensor1 = input_tensor1[0]
    if isinstance(input_tensor2,
                  Iterable) and not isinstance(input_tensor2, (str, bytes)):
        assert len(input_tensor2) == 1
        input_tensor2 = input_tensor2[0]
    name = ReturnOrAssignName(name, 'elementwise_mul_')
    return hbir_base.CreateElementwiseMul(
        input_tensor1, input_tensor2, name, enable_rounding,
        int32 if high_precision_output else int8, name + "_output")


def ElementwiseAdd(input_tensor1,
                   input_tensor2,
                   enable_rounding=False,
                   high_precision_output=False,
                   name='null'):
    if isinstance(input_tensor1,
                  Iterable) and not isinstance(input_tensor1, (str, bytes)):
        assert len(input_tensor1) == 1
        input_tensor1 = input_tensor1[0]
    if isinstance(input_tensor2,
                  Iterable) and not isinstance(input_tensor2, (str, bytes)):
        assert len(input_tensor2) == 1
        input_tensor2 = input_tensor2[0]
    name = ReturnOrAssignName(name, 'elementwise_add_')
    return hbir_base.CreateElementwiseAdd(
        input_tensor1, input_tensor2, name, enable_rounding,
        int32 if high_precision_output else int8, name + "_output")


def ElementwiseSub(input_tensor1,
                   input_tensor2,
                   enable_rounding=False,
                   output_type=int8,
                   name='null'):
    if isinstance(input_tensor1,
                  Iterable) and not isinstance(input_tensor1, (str, bytes)):
        assert len(input_tensor1) == 1
        input_tensor1 = input_tensor1[0]
    if isinstance(input_tensor2,
                  Iterable) and not isinstance(input_tensor2, (str, bytes)):
        assert len(input_tensor2) == 1
        input_tensor2 = input_tensor2[0]
    name = ReturnOrAssignName(name, 'elementwise_sub_')
    return hbir_base.CreateElementwiseSub(input_tensor1, input_tensor2, name,
                                          enable_rounding, output_type,
                                          name + "_output")


def ElementwiseDiv(input_tensor1,
                   input_tensor2,
                   enable_rounding=False,
                   output_type=int16,
                   name='null'):
    if isinstance(input_tensor1,
                  Iterable) and not isinstance(input_tensor1, (str, bytes)):
        assert len(input_tensor1) == 1
        input_tensor1 = input_tensor1[0]
    if isinstance(input_tensor2,
                  Iterable) and not isinstance(input_tensor2, (str, bytes)):
        assert len(input_tensor2) == 1
        input_tensor2 = input_tensor2[0]
    name = ReturnOrAssignName(name, 'elementwise_div_')
    return hbir_base.CreateElementwiseDiv(input_tensor1, input_tensor2, name,
                                          enable_rounding, output_type,
                                          name + "_output")


def SElementwiseDiv(input_tensors,
                    output_type=int8,
                    accu_right_shift=None,
                    output_scale=None,
                    output_right_shift=None,
                    enable_rounding=False,
                    table_param_is_str=False,
                    name='null'):
    if accu_right_shift is None:
        accu_right_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []
    assert output_type in [int8, int16]
    name = ReturnOrAssignName(name, 'elementwise_sdiv_')
    return hbir_base.CreateSElementwiseDiv(
        input_tensors[0], input_tensors[1], input_tensors[2], name,
        output_type, name + 'output', enable_rounding, table_param_is_str,
        output_scale, accu_right_shift, output_right_shift)


def StepwiseFit(input_tensor_name, boundary_table, output_table, name='null'):
    name = ReturnOrAssignName(name, 'stepwisefit_')
    return hbir_base.CreateStepwiseFitLayer(input_tensor_name, name,
                                            boundary_table, output_table, int8,
                                            name + "_output")


def SLut(input_tensor, out_type, attr, name='null'):
    name = ReturnOrAssignName(name, 'slut')
    return hbir_base.CreateSlutLayer(input_tensor, name, name + '_output',
                                     out_type, attr)


def Dilate(input_tensor, kernel=(3, 3), element_type='uint8', name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, 'dilate_')
    return hbir_base.CreateDilateLayer(input_tensor, name, kernel,
                                       element_type, int8, name + "_output")


def Reshape(input_tensor, mode, output_shape=(), name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, mode + '_')
    return hbir_base.CreateReshapeLayer(input_tensor, name, mode, output_shape,
                                        int8, name + "_output", [2, 2])


def Lut2(input_tensors, attr, name='null', output_type="int16"):
    assert len(input_tensors) == 1, "need 1 input"
    name = ReturnOrAssignName(name, 'lut2')
    return hbir_base.CreateLut2(input_tensors, name, name + '_output', attr,
                                output_type)


def LutFast(input_tensors, attr, name='null', output_type="int16"):
    assert len(input_tensors) == 1, "need 1 input"
    name = ReturnOrAssignName(name, 'lutfast')
    return hbir_base.CreateLutFast(input_tensors, name, name + '_output', attr,
                                   output_type)


def ElementwiseMin(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_min_')
    return hbir_base.CreateElementwiseMin(input_tensors, name,
                                          name + '_output')


def ElementwiseMax(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_max_')
    return hbir_base.CreateElementwiseMax(input_tensors, name,
                                          name + '_output')


def ElementwiseBitAnd(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_bit_and_')
    return hbir_base.CreateElementwiseBitAnd(input_tensors, name,
                                             name + '_output')


def ElementwiseBitOr(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_bit_or_')
    return hbir_base.CreateElementwiseBitOr(input_tensors, name,
                                            name + '_output')


def ElementwiseBitXor(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_bit_xor_')
    return hbir_base.CreateElementwiseBitXor(input_tensors, name,
                                             name + '_output')


def ElementwiseEqual(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_equal_')
    return hbir_base.CreateElementwiseEqual(input_tensors, name,
                                            name + '_output')


def ElementwiseNotEqual(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_not_equal_')
    return hbir_base.CreateElementwiseNotEqual(input_tensors, name,
                                               name + '_output')


def ElementwiseGreater(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_greater_')
    return hbir_base.CreateElementwiseGreater(input_tensors, name,
                                              name + '_output')


def ElementwiseLessOrEqual(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_less_or_equal_')
    return hbir_base.CreateElementwiseLessOrEqual(input_tensors, name,
                                                  name + '_output')


def ElementwiseGreaterOrEqual(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_greater_or_equal_')
    return hbir_base.CreateElementwiseGreaterOrEqual(input_tensors, name,
                                                     name + '_output')


def ElementwiseLess(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert len(input_tensors) > 1
    else:
        assert False, "need at least 2 inputs"
    name = ReturnOrAssignName(name, 'elementwise_less_')
    return hbir_base.CreateElementwiseLess(input_tensors, name,
                                           name + '_output')


def ElementwiseLogicalShift(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert input_tensors
    else:
        assert False, "need at least 1 inputs"
    name = ReturnOrAssignName(name, 'elementwise_logical_shift_')
    return hbir_base.CreateElementwiseLogicalShift(input_tensors, name,
                                                   name + '_output')


def ElementwiseArithShift(input_tensors, name='null'):
    if isinstance(input_tensors,
                  Iterable) and not isinstance(input_tensors, (str, bytes)):
        assert input_tensors
    else:
        assert False, "need at least 1 inputs"
    name = ReturnOrAssignName(name, 'elementwise_arith_shift_')
    return hbir_base.CreateElementwiseArithShift(input_tensors, name,
                                                 name + '_output')


def ElementwiseAbs(input_tensor, saturated_output=True, name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, 'abs')
    return hbir_base.CreateElementwiseAbs(input_tensor, name, saturated_output,
                                          name + "_output")


def ChannelShuffle(input_tensor, shuffle_index, name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, 'channelshuffle_')
    return hbir_base.CreateChannelShuffle(input_tensor, name, shuffle_index,
                                          name + "_output")


def Mean(input_tensor, dim=3, element_type=int8, name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    assert 0 <= dim < 4
    assert element_type in [int8, int16]
    name = ReturnOrAssignName(name, 'mean_')
    return hbir_base.CreateMeanLayer(input_tensor, name, dim, element_type,
                                     name + "_output")


def SMean(input_tensor,
          dim=3,
          element_type=int8,
          accu_right_shift=None,
          output_scale=None,
          output_right_shift=None,
          name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    assert 0 <= dim < 4
    assert element_type in [int8, int16]
    if accu_right_shift is None:
        accu_right_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []
    name = ReturnOrAssignName(name, 'smean_')
    return hbir_base.CreateSMeanLayer(input_tensor, name, dim, element_type,
                                      name + "_output", accu_right_shift,
                                      output_scale, output_right_shift)


def NearestUpsample(input_tensor, factor, name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    name = ReturnOrAssignName(name, "upsample_")
    if not isinstance(factor, Iterable):
        factor = [factor, factor]
    return hbir_base.CreateNearestUpsampleLayer(input_tensor, name, factor,
                                                int8, name + "_output")


def LayerNorm(input_tensors,
              gamma=None,
              gamma_shift=None,
              beta=None,
              beta_shift=None,
              output_type=int8,
              accu_right_shift=None,
              output_scale=None,
              output_right_shift=None,
              enable_rounding=False,
              table_param_is_str=False,
              name='null'):
    if gamma is None:
        gamma = []
    if gamma_shift is None:
        gamma_shift = []
    if beta is None:
        beta = []
    if beta_shift is None:
        beta_shift = []
    if accu_right_shift is None:
        accu_right_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []

    name = ReturnOrAssignName(name, "LayerNorm_")
    return hbir_base.CreateLayerNorm(
        input_tensors[0], input_tensors[1], name, gamma, beta, gamma_shift,
        beta_shift, output_type, enable_rounding, table_param_is_str,
        output_scale, accu_right_shift, output_right_shift, name + "_output")


def Softmax(input_tensor,
            preserve_shape=True,
            max_value_only=False,
            exp_table=None,
            exp_shift=0,
            output_type=float32,
            name='null'):
    if exp_table is None:
        exp_table = []
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    name = ReturnOrAssignName(name, "softmax_")
    return hbir_base.CreateSoftmax(
        input_tensor, name, preserve_shape, max_value_only, exp_table,
        exp_shift, 0, output_type, name + "_output", True, [], [], [])


def SoftmaxWithTable(input_tensor,
                     exp_table_tensor,
                     reciprocal_table_tensor,
                     preserve_shape=True,
                     max_value_only=False,
                     exp_table=None,
                     exp_shift=0,
                     middle_right_shift=0,
                     output_type=float32,
                     accu_right_shift=None,
                     output_scale=None,
                     output_right_shift=None,
                     table_param_is_str=False,
                     name='null'):
    if exp_table is None:
        exp_table = []
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    if isinstance(exp_table_tensor,
                  Iterable) and not isinstance(exp_table_tensor, (str, bytes)):
        assert len(exp_table_tensor) == 1
        exp_table_tensor = exp_table_tensor[0]
    if isinstance(reciprocal_table_tensor,
                  Iterable) and not isinstance(reciprocal_table_tensor,
                                               (str, bytes)):
        assert len(reciprocal_table_tensor) == 1
        reciprocal_table_tensor = reciprocal_table_tensor[0]
    if accu_right_shift is None:
        accu_right_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []
    assert output_type in [int8, int16]
    name = ReturnOrAssignName(name, "softmax_with_table_")
    return hbir_base.CreateSoftmaxWithTable(
        input_tensor, exp_table_tensor, reciprocal_table_tensor, name,
        preserve_shape, max_value_only, exp_table, exp_shift,
        middle_right_shift, output_type, name + '_output', True,
        table_param_is_str, output_scale, accu_right_shift, output_right_shift)


def ChannelMax(input_tensor,
               keep_score=True,
               keep_index=True,
               run_length_encoding=False,
               class_offset=0,
               group_number=1,
               name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    name = ReturnOrAssignName(name, "channelmax_")
    return hbir_base.CreateChannelMax(
        input_tensor, name, keep_score, keep_index, run_length_encoding,
        class_offset, group_number, name + "_output")


def Gemm(input_tensors,
         alpha,
         beta,
         is_transa,
         is_transb,
         is_literala=False,
         is_literalb=False,
         output_shape=(0, 0, 0, 0),
         output_type=int32,
         name='null'):
    assert isinstance(input_tensors, Iterable)
    name = ReturnOrAssignName(name, "gemm_")
    return hbir_base.CreateGemmLayer(
        input_tensors, name, alpha, beta, is_transa, is_transb, is_literala,
        is_literalb, output_shape, output_type, name + "_output")


def SGemm(input_tensors,
          alpha,
          beta,
          is_transa,
          is_transb,
          is_literala=False,
          is_literalb=False,
          output_shape=(0, 0, 0, 0),
          output_type=int32,
          output_scale=(),
          accu_right_shift=(),
          output_right_shift=(),
          enable_rounding=False,
          name='null'):
    assert isinstance(input_tensors, Iterable)
    name = ReturnOrAssignName(name, "sgemm_")
    return hbir_base.CreateSGemmLayer(
        input_tensors, name, alpha, beta, is_transa, is_transb, is_literala,
        is_literalb, output_shape, output_type, output_scale, accu_right_shift,
        output_right_shift, enable_rounding, name + '_output')


def Warping(input_tensors,
            stride,
            mapping_offset,
            kernel,
            warping_mode,
            is_mapping_y_then_x,
            is_input_uint8=False,
            is_output_uint8=False,
            padding_value=0,
            padding_value_uv=0,
            enable_rounding=True,
            interpolation_mode='bilinear',
            pad_mode='constant',
            name='null'):
    assert isinstance(input_tensors, Iterable)
    name = ReturnOrAssignName(name, "warping_")
    return hbir_base.CreateWarpingLayer(
        input_tensors, name, stride, mapping_offset, kernel, warping_mode,
        is_mapping_y_then_x, is_input_uint8, is_output_uint8, padding_value,
        padding_value_uv, enable_rounding, interpolation_mode, pad_mode, name)


def SConvolution(input_tensor,
                 sumin='null',
                 num_filter=1,
                 kernel=(1, 1),
                 stride=(1, 1),
                 pad=(0, 0),
                 dilation=(1, 1),
                 num_group=1,
                 use_bias=True,
                 use_relu=False,
                 output_type=int8,
                 weight_data=None,
                 bias_data=None,
                 accu_right_shift=None,
                 bias_left_shift=None,
                 output_scale=None,
                 output_right_shift=None,
                 sumin_scale=None,
                 sumin_left_shift=None,
                 enable_rounding=False,
                 name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]

    if weight_data is None:
        weight_data = []
    if bias_data is None:
        bias_data = []
    if accu_right_shift is None:
        accu_right_shift = []
    if bias_left_shift is None:
        bias_left_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []
    if sumin_scale is None:
        sumin_scale = []
    if sumin_left_shift is None:
        sumin_left_shift = []

    assert output_type in [int8, int16, int32]
    name = ReturnOrAssignName(name, 'conv_')
    return hbir_base.CreateSConvolutionLayer(
        input_tensor, name, num_filter, kernel, stride, pad, dilation,
        num_group, use_bias, use_relu, sumin, output_type, name + '_output',
        name + '_weight', weight_data, name + '_bias', bias_data,
        enable_rounding, accu_right_shift, bias_left_shift, output_scale,
        output_right_shift, sumin_scale, sumin_left_shift)  # pylint: disable=too-many-arguments


def SElementwiseMul(input_tensors,
                    output_type=int8,
                    accu_right_shift=None,
                    output_scale=None,
                    output_right_shift=None,
                    enable_rounding=False,
                    name='null'):
    if accu_right_shift is None:
        accu_right_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []
    assert output_type in [int8, int16, int32]
    name = ReturnOrAssignName(name, 'elementwisemul_')
    return hbir_base.CreateSElementwiseMul(
        input_tensors[0], input_tensors[1], name, enable_rounding, output_type,
        name + 'output', output_scale, accu_right_shift, output_right_shift)  # pylint: disable=too-many-arguments


def SElementwiseAdd(input_tensors,
                    output_type=int8,
                    accu_right_shift=None,
                    output_scale=None,
                    output_right_shift=None,
                    input_left_shift=None,
                    sumin_scale=None,
                    sumin_left_shift=None,
                    enable_rounding=False,
                    name='null'):
    if accu_right_shift is None:
        accu_right_shift = []
    if output_scale is None:
        output_scale = []
    if output_right_shift is None:
        output_right_shift = []
    if input_left_shift is None:
        input_left_shift = []
    if sumin_scale is None:
        sumin_scale = []
    if sumin_left_shift is None:
        sumin_left_shift = []
    name = ReturnOrAssignName(name, "SElementwise_Add_")
    return hbir_base.CreateSElementwiseAdd(
        input_tensors[0], input_tensors[1], name, enable_rounding, output_type,
        name + '_output', output_scale, accu_right_shift, output_right_shift,
        input_left_shift, sumin_scale, sumin_left_shift)


def Tile(input_tensor, dim, multiples, name='null'):
    if isinstance(input_tensor,
                  Iterable) and not isinstance(input_tensor, (str, bytes)):
        assert len(input_tensor) == 1
        input_tensor = input_tensor[0]
    name = ReturnOrAssignName(name, "tile_")
    return hbir_base.CreateTileLayer(input_tensor, name, dim, multiples, name)


def ReduceMax(input_tensor, reduce_axis, return_index=False, name='null'):
    name = ReturnOrAssignName(name, "reducemax_")
    return hbir_base.CreateReduceMaxLayer(input_tensor, name, reduce_axis,
                                          return_index, name + "_output")


def ReduceMin(input_tensor, reduce_axis, return_index=False, name='null'):
    name = ReturnOrAssignName(name, "reducemin_")
    return hbir_base.CreateReduceMinLayer(input_tensor, name, reduce_axis,
                                          return_index, name + "_output")


def View(input_tensor, expected_shape, name='null'):
    name = ReturnOrAssignName(name, "view_")
    return hbir_base.CreateViewLayer(input_tensor, name, expected_shape,
                                     name + "_output")


def Transpose(input_tensor, perm, name='null'):
    name = ReturnOrAssignName(name, "transpose_")
    return hbir_base.CreateTransposeLayer(input_tensor, name, perm,
                                          name + "_output")


def Crop(input_tensor, rect, name='null'):
    name = ReturnOrAssignName(name, "crop_")
    return hbir_base.CreateCropLayer(input_tensor, name, rect,
                                     name + "_output")


def Rle(input_tensor, output_type=int8, name='null'):
    name = ReturnOrAssignName(name, "rle_")
    return hbir_base.CreateRleLayer(input_tensor, name, output_type,
                                    name + "_output")


def Scatter(input_tensors, out_shape, name='null'):
    name = ReturnOrAssignName(name, "scatter_")
    return hbir_base.CreateScatterLayer(input_tensors[0], input_tensors[1],
                                        out_shape, name, name + "_output")


def Roll(input_tensor, shifts, dims, name='null'):
    name = ReturnOrAssignName(name, "roll_")
    return hbir_base.CreateRollLayer(input_tensor, shifts, dims, name,
                                     name + "_output")


def Gather(input_tensors,
           name='null',
           voxel_size=None,
           coors_range=None,
           max_points=None,
           max_voxels=None):
    name = ReturnOrAssignName(name, "gather_")
    return hbir_base.CreateGatherLayer(input_tensors[0], name, voxel_size,
                                       coors_range, max_points, max_voxels,
                                       name + "_output0", name + "_output1")


def OnnxGather(input_tensor,
               indices='null',
               indices_shape=None,
               indices_data=None,
               axis=None,
               name='null'):
    name = ReturnOrAssignName(name, "onnxgather_")
    if indices_data is None:
        indices_data = []
    if axis is None:
        axis = 0
    if indices == 'null':
        return hbir_base.CreateOnnxGatherLayer(
            input_tensor, name, name + "_indices", indices_shape, indices_data,
            axis, name + "_output")

    return hbir_base.CreateOnnxGatherLayer(input_tensor, indices, name, axis,
                                           name + "_output")


def GatherElements(input_tensor, indices, axis: int32, name='null'):
    name = ReturnOrAssignName(name, "gather_elements_")
    if axis is None:
        axis = 0
    return hbir_base.CreateGatherElementsLayer(input_tensor, indices, name,
                                               axis, name + "_output")


def Clamp(input_tensor,
          lower_bound,
          upper_bound,
          output_type=int8,
          name='null'):
    """
    lower_bound: lower-bound of the range to be clamped to
    upper_bound: uper-bound of the range to be clameped to
    lower_bound, upper_bound could be a literal, tensor, or None
    use a INT32_MAX to distinguish if min/max set to None
    INT32_MAX: 2147483647
    """
    name = ReturnOrAssignName(name, "clamp_")
    int_max = 2147483647
    min_val = int_max
    max_val = int_max
    min_tensor = ''
    max_tensor = ''

    if isinstance(lower_bound, int):
        min_val = lower_bound
    elif isinstance(lower_bound, str):
        min_tensor = lower_bound

    if isinstance(upper_bound, int):
        max_val = upper_bound
    elif isinstance(upper_bound, str):
        max_tensor = upper_bound

    return hbir_base.CreateClampLayer(input_tensor, min_tensor, max_tensor,
                                      name, min_val, max_val, output_type,
                                      name + "_output")


def TopK(input_tensor,
         k,
         dim=0,
         largest=True,
         sorted=True,
         index=True,
         index_type=int32,
         name='null'):
    name = ReturnOrAssignName(name, "topk_")
    return hbir_base.CreateTopKElementsLayer(input_tensor, name, k, dim,
                                             largest, sorted, index,
                                             index_type, name + "_output")
