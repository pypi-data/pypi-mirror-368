"""
Convert NDArray in MXNET format to hardware layout
"""

import abc
from typing import List, Union
import numpy as np
import hbdk.config

try:
    import mxnet as mx  # pylint: disable=unused-import
except ImportError:
    pass


class NDArrayBPULayoutConversion:
    """
    Convert an ndarray, which is the output of the specific operator.
    """
    __metaclass = abc.ABCMeta  # pylint: disable=invalid-name

    op: List[str] = []  # The list of Operator name to match
    marches: List[str] = []  # Affected march names

    def __init__(self, sym: 'mx.symbol', march: str, sym_type: str,
                 attr_dict: dict):
        """
        :param sym: The op symbol
        :param march: The hardware march name
        :param sym_type: The symbol name
        :param attr_dict: The attribute dictionary
        """
        self.sym = sym
        self.march = hbdk.config.get_normalized_march(march)
        # assert hbdk.config.is_march_supported(self.march)
        self.sym_type = sym_type
        self.attr_dict = attr_dict

    @abc.abstractmethod
    def to_hardware_layout(self, arrays: List[np.ndarray]):
        """
        Convert NDArray from framework format to hardware format
        :param arrays: The ndarray value of the op outputs
        :return: The NDArray in hardware layout.
        Dimension/dtype/value may different from self.a
        """
        pass  # pylint: disable=unnecessary-pass

    @abc.abstractmethod
    def to_framework_layout(self, arrays: List[np.ndarray]):
        """
        Convert from hardware format to framework format
        This is mostly for the debugging purpose.
        :param arrays: The ndarray value of the op output
        :return: The NDArray in framework layout.
        Dimension/dtype/value may different from self.a
        """
        pass  # pylint: disable=unnecessary-pass


def precision_cast(dtype: Union[str, np.dtype], x: int):
    """
    Convert x to given dtype, and assert there is no overflow or underflow
    """
    dtype = np.dtype(dtype)
    min_ = np.iinfo(dtype).min
    max_ = np.iinfo(dtype).max
    assert min_ <= x <= max_, \
        "input value out of bound during precision cast." \
        " Min=%s, Max=%s, x=%s" % (str(min_), str(max_), str(x))
    r = dtype.type(x)
    return r


def convert_to_hardware_layout(sym: 'mx.symbol', outputs: List[np.ndarray],
                               march: str, sym_type: str, attr_dict: dict):
    """
    :param sym: Mxnet symbol
    :param outputs: The list of symbol outputs
    :param march: The current hardware march, str
    :return: The converted outputs
    """
    from .dpp import DppRcnnNDArrayBPULayoutConversion
    from .channel_argmax import ChannelArgmaxNDArrayBPULayoutConversion
    handlers = {
        DppRcnnNDArrayBPULayoutConversion,
        ChannelArgmaxNDArrayBPULayoutConversion
    }
    patterns = {}
    for h in handlers:
        for op_type in h.op:
            patterns[op_type] = h
    if sym_type in patterns:
        convert = patterns[sym_type](sym, march, sym_type, attr_dict)
        return convert.to_hardware_layout(outputs)
    return None
