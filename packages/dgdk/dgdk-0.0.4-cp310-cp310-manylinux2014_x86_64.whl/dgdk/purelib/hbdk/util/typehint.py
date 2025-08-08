# pylint: skip-file
r"""
Type hints utilities
"""

from typing import Union, Sequence, Dict
import typing.io as tio
#
# try:
#     import mxnet as mx
# except:
#     mx = None
#
# try:
#     from horizon_plugin_tensorflow.hbdk_tf import hbdk_tf
#     import tensorflow as tf
# except ImportError:
#     hbdk_tf = False
#     tf = None
r"""The inputs shapes. Can be one of the following:
1. Comma separated string of NxHxWxC: "1x2x3x4,4x5x6x7"
2. Iterable of comma separated string. ["1x2x3x4", "4x5x6x7"]
3. Iterable of shape (For single shape): [1, 2, 3, 4]
4. Iterable of iterable of shapes (for multiple shapes): [[1, 2, 3, 4], [4, 5, 6, 7]]
"""
ShapeT = Union[str, Sequence[str], Sequence[int], Sequence[Sequence[int]]]
r"""The path to Mxnet symbol json or Mxnet symbol object
"""
MxnetSymOrFileT = Union[str, 'mx.symbol']
r"""The path to Mxnet param file or Dictionary of Mxnet ndarray
"""
MxnetParamOrFileT = Union[str, Dict[str, 'mx.ndarray.ndarray.NDArray']]
r"""The path to Tensorflow protobuf file or TF GraphDef
"""
TfGraphOrFileT = Union[str, 'tf.GraphDef']

StrOrListT = Union[str, Sequence[str]]
