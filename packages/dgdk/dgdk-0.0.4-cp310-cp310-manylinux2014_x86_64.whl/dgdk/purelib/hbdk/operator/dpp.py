"""
Convert dpp output between hardware layout and framework layout
"""

from typing import List
import numpy as np
from .conversion import NDArrayBPULayoutConversion, precision_cast


class DppRcnnNDArrayBPULayoutConversion(NDArrayBPULayoutConversion):
    """
    Convert Dpp/Rcnn (DetectionPostProcess/RcnnPostProcess)
     result between hardware and framework layout.

    .. rubric:: Framework layout

        There are 6 channels, which are the coordinate of the box
        in the origin pictures (x1, y1, x2, y2),
        and the score, and the classification index.
        The element type of each number are the same,
        which is usually int16 or int8


    .. rubric:: Hardware layout

        If the framework input is float32,
        Just add one row of number of boxes, the following does not apply

        The output dtype is int16, and the return value
        contains 10 channels. (10 bytes)
        For the real hardware, there are usually 6 channel padding
        following the 10 channel data,
        But it's possible to have more padding.
        In a word, a values after channel 10 should be ignored.

        Also, the hardware output has one extra row indicates how many valid
        boxes (multiplied by 16) inside the output, in the following format

        bytes0-1 (num_box * 16, int16, little endian)
        bytes2-9 (padding, all zeros)

        The content 5 channels (5*int16=10 bytes).

        bytes0-1 (x1, int16, little endian)
        bytes2-3 (y1, int16, little endian)
        bytes4-5 (x2, int16, little endian)
        bytes6-7 (y2, int16, little endian)
        byte8    (score, int8)
        byte9    (classification index, uint8)
    """

    # TODO(hehaoqian): Use Python decoration to register operators
    op = [
        "DetectionPostProcessing_X2",  # Mxnet dpp
        "BpuQuantiProposal",  # TF dpp
        "RCNNPostProcessing_X2",  # Mxnet Rcnn
        "BpuPostProcessRcnn",  # TF Rcnn
        "proposal",  # Pytorch dpp
    ]

    dpp_ops = [
        "DetectionPostProcessing_X2",  # Mxnet dpp
        "BpuQuantiProposal",  # TF dpp
    ]
    marches = []

    def to_hardware_layout(self, arrays: List[np.ndarray]):
        results = []
        assert arrays and len(arrays) <= 2
        for arr_idx, a in enumerate(arrays):
            a = arrays[arr_idx]
            shape = a.shape
            dtype = np.dtype(a.dtype)
            assert shape[-1] == 6
            assert dtype.itemsize >= 2
            oshape = list(shape)
            oshape[-2] += 1
            padding_value = int(self.attr_dict["ignore_value"]) \
                if "ignore_value" in self.attr_dict else -1
            if arr_idx == 0:
                oshape[-1] = 10
                r = np.ones(oshape, np.int8) * padding_value
            elif self.sym_type in type(self).dpp_ops:
                oshape[-1] = 10
                r = np.ones(oshape, np.int8) * padding_value
            else:
                assert dtype == np.dtype('float32')
                r = np.ones(oshape, dtype) * padding_value
            batch = shape[0]
            a = a.reshape((batch, -1, shape[-1]))
            r = r.reshape((batch, -1, oshape[-1]))

            def split_int16(x):
                assert x & 0xffff0000 == 0 \
                       or x & 0xffff0000 & 0xffffff00 == 0xffff0000, \
                    "%d is out of range" % x
                return np.int8(x & 0xff), np.int8((x >> 8) & 0xff)

            for i in range(batch):
                num_box = 0
                for j in range(a.shape[1]):
                    asub = a[i, j]
                    rsub = r[i, j + 1]
                    x1, y1, x2, y2 = asub[0], asub[1], asub[2], asub[3]
                    score = asub[4]
                    cls_idx = asub[5]
                    if x1 == y1 == x2 == y2 == score \
                            == cls_idx == padding_value:
                        continue
                    num_box += 1
                    if arr_idx == 0 or (self.sym_type in type(self).dpp_ops):
                        rsub[0], rsub[1] = split_int16(x1)
                        rsub[2], rsub[3] = split_int16(y1)
                        rsub[4], rsub[5] = split_int16(x2)
                        rsub[6], rsub[7] = split_int16(y2)
                        rsub[8] = precision_cast('int8', score)
                        rsub[9] = precision_cast('uint8', cls_idx)
                    else:
                        rsub[:] = asub[:]
                byte_per_row = 16
                if dtype == np.dtype("float32"):
                    byte_per_row = 24
                if arr_idx == 0 or (self.sym_type in type(self).dpp_ops):
                    r[i, 0, 0], r[i, 0, 1] = split_int16(
                        num_box * byte_per_row)
                    r[i, 0, 2:] = 0
                else:
                    r[i, 0, 0] = num_box * byte_per_row
                    r[i, 0, 1:] = 0
            r = r.reshape(oshape)
            if arr_idx == 0 or self.sym_type in type(self).dpp_ops:
                # Convert to int16
                shape = list(r.shape)
                shape[-1] //= 2
                r = np.frombuffer(r.tobytes(), dtype=np.int16)
                r = r.reshape(shape)
            results.append(r)

        return results

    def to_framework_layout(self, arrays: List[np.ndarray]):
        results = []
        assert arrays and len(arrays) <= 2
        for arr_idx, a in enumerate(arrays):
            a = arrays[arr_idx]
            dtype = np.dtype(a.dtype)
            shape = list(a.shape)
            if arr_idx == 0 or (self.sym_type in type(self).dpp_ops):
                assert a.dtype.name == 'int16'
                shape[-1] *= 2
                # Convert input from int16 to int8 for easier processing
                a = np.frombuffer(a.tobytes(), dtype=np.int8)
                assert shape[-1] >= 10
            else:
                assert a.dtype.name == 'float32'
            a = a.reshape(shape)
            oshape = list(shape)
            oshape[-1] = 6
            oshape[-2] -= 1
            padding_value = int(self.attr_dict["ignore_value"]) \
                if "ignore_value" in self.attr_dict else -1
            if arr_idx == 0 or (self.sym_type in type(self).dpp_ops):
                r = np.ones(oshape, np.int32) * padding_value
            else:
                r = np.ones(oshape, np.float32) * padding_value
            batch = shape[0]
            a = a.reshape((batch, -1, shape[-1]))
            r = r.reshape((batch, -1, oshape[-1]))

            def to_int16(lsb, msb):
                assert lsb & 0xffffff00 == 0 \
                       or lsb & 0xffffff00 & 0xffffff00 == 0xffffff00
                assert msb & 0xffffff00 == 0 \
                       or msb & 0xffffff00 & 0xffffff00 == 0xffffff00
                return np.int16(np.uint8(lsb) + np.uint8(msb) * 256)

            def to_uint16(lsb, msb):
                assert lsb & 0xffffff00 == 0 \
                       or lsb & 0xffffff00 & 0xffffff00 == 0xffffff00
                assert msb & 0xffffff00 == 0 \
                       or msb & 0xffffff00 & 0xffffff00 == 0xffffff00
                return np.uint16(np.uint8(lsb) + np.uint8(msb) * 256)

            for i in range(batch):
                byte_per_row = 16
                if dtype == np.dtype("float32"):
                    byte_per_row = 24
                if arr_idx == 0 or (self.sym_type in type(self).dpp_ops):
                    num_box = to_uint16(a[i, 0, 0], a[i, 0, 1])
                else:
                    num_box = int(a[i, 0, 0])
                assert num_box % byte_per_row == 0
                num_box //= byte_per_row
                assert num_box >= 0
                for j in range(a.shape[1] - 1):
                    asub = a[i, j + 1]
                    rsub = r[i, j]
                    if j < num_box:
                        if arr_idx == 0 or (
                                self.sym_type in type(self).dpp_ops):
                            x1 = to_int16(asub[0], asub[1])
                            y1 = to_int16(asub[2], asub[3])
                            x2 = to_int16(asub[4], asub[5])
                            y2 = to_int16(asub[6], asub[7])
                            score = np.int8(asub[8])
                            cls_idx = np.uint8(asub[9])
                        else:
                            x1, y1, x2, y2, score, cls_idx = asub[0], asub[
                                1], asub[2], asub[3], asub[4], asub[5]
                    else:
                        x1 = padding_value
                        y1 = padding_value
                        x2 = padding_value
                        y2 = padding_value
                        score = padding_value
                        cls_idx = padding_value
                    rsub[0], rsub[1], rsub[2], rsub[3] = x1, y1, x2, y2
                    rsub[4] = score
                    rsub[5] = cls_idx
                    # if j < num_box:
                    #    for k in range(6):
                    #        assert rsub[k] != padding_value

            r = r.reshape(oshape)
            results.append(r)
        return results
