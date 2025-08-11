## AUTOMATICALLY GENERATED. DO NOT EDIT
"""
Convert channel_argmax output between hardware layout and framework layout
"""
from typing import List
import numpy as np
from hbdk.config import March
from .conversion import NDArrayBPULayoutConversion


class ChannelArgmaxNDArrayBPULayoutConversion(NDArrayBPULayoutConversion):
    """
    Convert channel_argmax result between hardware
    and framework layout.
    .. rubric:: Framework layout
    .. rubric:: Hardware layout
    """
    op = [
        "channel_argmax",  # in mxnet, different layout
        "BpuPostProcessChannelArgmax",  # in tf plugin, different layout
        "ParsingPostProcessing_X2",  # in mxnet, same layout
    ]

    def to_hardware_layout(self, arrays: List[np.ndarray]):
        if self.sym_type == "ParsingPostProcessing_X2":
            return arrays
        keep_score = self.attr_dict[
            "keep_score"] if "keep_score" in self.attr_dict else "True"
        group_num = int(self.attr_dict["group_num"] if "group_num" in
                        self.attr_dict else "1")
        if keep_score == "False" and group_num == 1:
            return arrays
        a = arrays[0]
        if keep_score == "True":
            assert len(
                arrays
            ) == 2, "Framework should have two outputs." " One for index and the other for score"
            b = arrays[1]
        else:
            assert len(
                arrays) == 1, "Framework should have one output (index)."
            b = arrays[0]
        assert a.shape == b.shape and a.dtype == b.dtype, "The shape and dtype of two framework outputs should be the same"
        assert a.shape[
            -1] == group_num, "The input channel should be equal to group_num in symbol attr"
        dtype = np.dtype(a.dtype)
        if False:  # pylint: disable=W
            pass  # pylint: disable=W
        elif self.march in (March.BAYES, March.B25E, March.B253):
            if keep_score == "True":
                b = arrays[1]
                oshape = list(a.shape)
                oshape[-1] = 2 * group_num
                a = a.reshape([-1, a.shape[-1]])
                b = b.reshape([-1, b.shape[-1]])
                r = np.zeros(oshape, dtype)
                r = r.reshape([-1, oshape[-1]])
                for i in range(a.shape[0]):
                    for c in range(a.shape[-1]):
                        idx = a[i, c]
                        score = b[i, c]
                        r[i, 2 * c + 0] = idx
                        r[i, 2 * c + 1] = score
                r = r.reshape(oshape)
            else:
                r = a
        elif self.march == March.BERNOULLI:
            oshape = list(a.shape)
            oshape[-3] *= group_num
            if keep_score == "True":
                oshape[-1] = 2
            else:
                oshape[-1] = 1
            a = a.reshape([-1, a.shape[-2], a.shape[-1]])
            b = b.reshape([-1, b.shape[-2], b.shape[-1]])
            r = np.zeros(oshape, dtype)
            r = r.reshape([-1, oshape[-2], oshape[-1]])
            for i in range(a.shape[0]):
                for w in range(a.shape[1]):
                    for c in range(a.shape[-1]):
                        idx = a[i, w, c]
                        score = b[i, w, c]
                        r[i * group_num + c, w, 0] = idx
                        if keep_score == "True":
                            r[i * group_num + c, w, 1] = score
            r = r.reshape(oshape)
        elif self.march == March.BERNOULLI2:
            oshape = list(a.shape)
            oshape[-3] *= group_num
            if keep_score == "True":
                oshape[-1] = 2
            else:
                oshape[-1] = 1
            a = a.reshape([-1, a.shape[-2], a.shape[-1]])
            b = b.reshape([-1, b.shape[-2], b.shape[-1]])
            r = np.zeros(oshape, dtype)
            r = r.reshape([-1, oshape[-2], oshape[-1]])
            for i in range(a.shape[0]):
                for w in range(a.shape[1]):
                    for c in range(a.shape[-1]):
                        idx = a[i, w, c]
                        score = b[i, w, c]
                        r[i * group_num + c, w, 0] = idx
                        if keep_score == "True":
                            r[i * group_num + c, w, 1] = score
            r = r.reshape(oshape)
        else:
            raise NotImplementedError("channel_argmax not implemented for ",
                                      self.march)
        return [r]

    def to_framework_layout(self, arrays: List[np.ndarray]):
        group_num = int(self.attr_dict["group_num"] if "group_num" in
                        self.attr_dict else "1")
        assert len(arrays) == 1
        if self.sym_type == "ParsingPostProcessing_X2":
            return arrays
        a = arrays[0]
        shape = a.shape
        oshape = list(shape)
        dtype = arrays[0].dtype
        if False:  # pylint: disable=W
            pass  # pylint: disable=W
        elif self.march == March.BERNOULLI:
            assert shape[-3] % group_num == 0
            assert shape[-1] == 2
            oshape = list(shape)
            oshape[-1] = group_num
            oshape[-3] //= group_num
            a = a.reshape([-1, shape[-2], shape[-1]])
            r = np.zeros(oshape, dtype)
            r = r.reshape([-1, oshape[-2], oshape[-1]])
            s = np.zeros(oshape, dtype)
            s = s.reshape([-1, oshape[-2], oshape[-1]])
            for i in range(a.shape[0]):
                for w in range(a.shape[1]):
                    idx = a[i, w, 0]
                    score = a[i, w, 1]
                    r[i // group_num, w, i % group_num] = idx
                    s[i // group_num, w, i % group_num] = score
            r = r.reshape(oshape)
            s = s.reshape(oshape)
        elif self.march == March.BERNOULLI2:
            assert shape[-3] % group_num == 0
            assert shape[-1] == 2
            oshape = list(shape)
            oshape[-1] = group_num
            oshape[-3] //= group_num
            a = a.reshape([-1, shape[-2], shape[-1]])
            r = np.zeros(oshape, dtype)
            r = r.reshape([-1, oshape[-2], oshape[-1]])
            s = np.zeros(oshape, dtype)
            s = s.reshape([-1, oshape[-2], oshape[-1]])
            for i in range(a.shape[0]):
                for w in range(a.shape[1]):
                    idx = a[i, w, 0]
                    score = a[i, w, 1]
                    r[i // group_num, w, i % group_num] = idx
                    s[i // group_num, w, i % group_num] = score
            r = r.reshape(oshape)
            s = s.reshape(oshape)
        else:
            raise NotImplementedError("channel_argmax not implemented for ",
                                      self.march)
        return [r, s]
