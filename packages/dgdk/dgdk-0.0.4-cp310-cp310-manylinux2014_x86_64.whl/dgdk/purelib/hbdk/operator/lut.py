r"""
Special handling of the Lut Operator
"""

from ctypes import cdll, c_float
import sys
import math
from typing import List

# LUTType
K_SIGMOID = 0
K_TANH = 1
K_EXP = 2
K_LOG = 3

# LUTOutType
K_INT8 = 0
K_INT16 = 1

if sys.platform.startswith('linux'):
    libm = cdll.LoadLibrary("libm.so.6")
elif sys.platform.startswith('darwin'):
    libm = cdll.LoadLibrary("libm.dylib")
else:
    assert sys.platform.startswith("win")
    libm = cdll.LoadLibrary("api-ms-win-crt-math-l1-1-0.dll")

libm_roundf = libm.roundf
libm_roundf.restype = c_float


def c_roundf(x: float) -> float:
    """A stupid workaround to get C roundf() function.
    Python round() does not work exactly the same as C/C++ roundf"""
    return libm_roundf(c_float(x))


def sigmoid(x: float) -> float:
    """double sigmoid(double x)"""
    return 1.0 / (1 + math.exp(-x))


def tanh(x: float) -> float:
    """double tanh(double x)"""
    a = math.exp(x)
    b = math.exp(-x)
    return (a - b) / (a + b)


def get_value(val: float, compute_type: int) -> float:  # pylint: disable=R1710
    """double GetValue(double f, int type)"""
    if compute_type == K_SIGMOID:
        return sigmoid(val)
    if compute_type == K_TANH:
        return tanh(val)
    if compute_type == K_EXP:
        return math.exp(val)
    if compute_type == K_LOG:
        return math.log(val)
    assert False, "Unsupported value_type %s" % str(compute_type)


def get_symmetry_value(x: int, compute_type: int, oshift: int) -> int:  # pylint: disable=R1710
    """GetSymmetryValue(int x, int type, int oshift)"""
    # pylint: disable=inconsistent-return-statements
    if compute_type == K_SIGMOID:
        return (1 << oshift) - x
    if compute_type == K_TANH:
        return -x
    assert False, "not supported lut type %s" % str(compute_type)


def quantize_x(x: float, shift: int, precise: bool):
    """float QuantizeX(float x, int shift, int* q, bool precise)"""
    q = c_roundf(x * (1 << shift))
    if precise:
        return q, q * math.pow(2, -shift)
    return q, x


def int16_bound(b: int) -> int:
    """int int16Bound(int b)"""
    shift = 0
    while b < -32768 or b > 32767:
        b = b // 2
        shift += 1
    return b * (1 << shift)


def quantize_line(slope: float,
                  beta: float,
                  bits: int = 15,
                  max_shift: int = 31) -> (int, int, int):
    """void QuantizeLine(slope, beta, int* k, int* kshift, int* b, int bits=15)"""
    kf, shift = math.frexp(slope)
    k = min(c_roundf(kf * (1 << bits)), (1 << bits) - 1)
    k = max(k, -(1 << bits) + 1)
    kshift = bits - shift

    def shift_float(x):
        if kshift >= 0:
            return x * (1 << kshift)
        return x / (1 << (-kshift))

    if kshift > max_shift:
        bf, shift = math.frexp(beta)
        k = 0
        kshift = bits - shift
        if kshift > max_shift:
            kshift = max_shift
        assert abs(shift_float(bf)) <= ((1 << 31) - 1)
        b = c_roundf(shift_float(bf))
    else:
        assert abs(shift_float(beta)) <= ((1 << 31) - 1)
        b = c_roundf(shift_float(beta))
    b = int16_bound(b)
    return k, kshift, b


def y_max(compute_type: int, xmin: float, xmax: float) -> float:
    """float YMax(int type, float xmin, float xmax)"""
    return max(
        math.fabs(get_value(xmin, compute_type)),
        math.fabs(get_value(xmax, compute_type)))


def init_lut(compute_type: int, xmin: float, xmax: float, ymax: float,
             n: int) -> (List[int], int, int, int, int):
    """void InitLUT(int type, float xmin, float xmax, float ymax,
       int n, int* table, int* tshift, int* k, int* b, int* kshift, double* buff"""

    assert int(n) == n, "n must be integer"
    table = [0] * n
    buff = [0] * n
    res = 0.0
    f = 0.0
    step = (xmax - xmin) / (n - 1)
    for i in range(n):
        f = xmin + i * step
        res = get_value(f, compute_type)
        buff[i] = res
    kf = 0.0
    bf = 0.0
    ys = 0
    kf = (n - 1) / (xmax - xmin)
    bf = (-xmin) * (n - 1) / (xmax - xmin)
    k, kshift, b = quantize_line(kf, bf)
    _, ys = math.frexp(ymax)
    tshift = 15 - ys
    assert tshift >= 0, "tshift=%d must be >=0" % tshift
    for i in range(n):
        table[i] = c_roundf(buff[i] * (1 << tshift))
        table[i] = max(table[i], -(1 << 15))
        table[i] = min(table[i], (1 << 15) - 1)
    return table, tshift, k, b, kshift, buff


def table_lookup(x: int, ishift: int, idx_bits: int, scale: int,
                 scale_shift: int, beta: int, table: List[int], n: int) -> int:
    """int TableLookUp(int x, int ishift, int idx_bits, int scale,
       int scale_shift, int beta, int table, int n"""
    assert scale_shift - idx_bits >= 0
    assert scale_shift + ishift - idx_bits <= 31
    findex = (x * scale + beta *
              (1 << ishift)) >> (scale_shift + ishift - idx_bits)
    index = findex >> idx_bits
    diff = findex - (index << idx_bits)
    full = 1 << idx_bits
    if index >= 0 and index + 1 < n:
        ret = table[index] * (full - diff) + table[index + 1] * diff
        return ret >> idx_bits
    if index < 0:
        index = 0
    elif index + 1 > n:
        index = n - 1
    return table[index]


def init_line(compute_type: int, x: float, bound_x: float) -> (int, int, int):
    """void InitLine(int type, float x, float bound_x, int* k, int* kshift, int* b"""
    y = get_value(x, compute_type)
    bound_y = get_value(bound_x, compute_type)
    slope = (y - bound_y) / (x - bound_x)
    beta = -slope * bound_x + bound_y
    return quantize_line(slope, beta)


def line_fit(x: int, ishift: int, out_shift: int, k: int, kshift: int,
             b: int) -> int:
    """int LineFit(int x, int ishift, int out_shift, int k, int kshift, int b)"""
    assert kshift + ishift - out_shift <= 31
    v = (x * k + b * (1 << ishift)) >> (kshift + ishift - out_shift)
    v = max(v, -(1 << 15))
    v = min(v, (1 << 15) - 1)
    return v


class LUTParam:
    """class to record lut params"""

    def __init__(self, lut_type: int, sparse_min: float, sparse_max: float,
                 ymax: float, sparse_steps: int, dense_min: float,
                 dense_max: float, dense_steps: int, x_min: float,
                 x_max: float, idx_bits: int, symmetry: bool, data_shift: int,
                 shared_table: bool, pointwise_shift: bool):
        self.lut_type = lut_type
        self.sparse_min = sparse_min
        self.sparse_max = sparse_max
        self.ymax = ymax
        self.sparse_steps = sparse_steps
        self.dense_min = dense_min
        self.dense_max = dense_max
        self.dense_steps = dense_steps
        self.x_min = x_min
        self.x_max = x_max
        self.idx_bits = idx_bits
        self.symmetry = symmetry
        self.data_shift = data_shift
        self.shared_table = shared_table
        self.pointwise_shift = pointwise_shift


def init(param: LUTParam, input_shift: int = 255):
    # pylint: disable=unused-variable
    """Init LUT axuiliary states.
       Return values are in the order of std::vector<std::string>
       ListAuxiliaryStates()
    """
    if input_shift == 255:
        data_shift = param.data_shift
    else:
        data_shift = input_shift

    relaxed_bound = param.shared_table or param.pointwise_shift
    sparse_min_dptr, sparse_fmin = quantize_x(param.sparse_min, data_shift,
                                              not relaxed_bound)
    sparse_max_dptr, sparse_fmax = quantize_x(param.sparse_max, data_shift,
                                              not relaxed_bound)
    dense_min_dptr, dense_fmin = quantize_x(param.dense_min, data_shift,
                                            not relaxed_bound)
    dense_max_dptr, dense_fmax = quantize_x(param.dense_max, data_shift,
                                            not relaxed_bound)
    x_min_dptr, x_fmin = quantize_x(param.x_min, data_shift, not relaxed_bound)
    x_max_dptr, x_fmax = quantize_x(param.x_max, data_shift, not relaxed_bound)
    left_min = min(sparse_fmin, dense_fmin)
    right_max = max(sparse_fmax, dense_fmax)

    if param.sparse_min > param.dense_max \
            or param.sparse_max < param.dense_min:
        assert False, "not valid min max for dense and sparse tables"
    if param.sparse_min >= param.sparse_max \
            or param.dense_min >= param.dense_max:
        assert False, "not valid min max for LUT"
    if not (param.x_min <= param.dense_min
            and param.x_min <= param.sparse_min):
        assert False, "not valid min_x for LUT"
    if not (param.x_max >= param.dense_max
            and param.x_max >= param.sparse_max):
        assert False, "not valid max_x for LUT"

    if param.symmetry:
        assert param.lut_type == K_SIGMOID or param.lut_type == K_TANH
        assert param.sparse_min >= 0, "sparse_min should be non-negative"
        assert param.dense_min >= 0, "dense_min should be non-negative"

    ymax = y_max(param.lut_type, dense_fmin, dense_fmax)
    ymax = max(ymax, y_max(param.lut_type, sparse_fmin, sparse_fmax))
    ymax = max(ymax, y_max(param.lut_type, x_fmin, x_fmax))
    # if ymax > param.ymax:
    #    print("ymax is smaller than absolute y values of tables,"
    #          " set ymax automatically, which is " + str(ymax))
    ymax = max(param.ymax, ymax)
    sparse_table_dptr, sparse_out_shift, sparse_scale_dptr, \
    sparse_beta_dptr, sparse_shift_dptr, sparse_buff_dptr = \
        init_lut(param.lut_type, sparse_fmin, sparse_fmax, ymax, 256)
    dense_table_dptr, dense_out_shift, dense_scale_dptr, \
    dense_beta_dptr, dense_shift_dptr, dense_buff_dptr = \
        init_lut(param.lut_type, dense_fmin, dense_fmax, ymax, 256)
    assert dense_out_shift == sparse_out_shift, \
        " shift for dense and sparse table must be equal"

    out_shift_dptr = dense_out_shift

    left_scale_dptr, left_shift_dptr, left_beta_dptr = init_line(
        param.lut_type, x_fmin, left_min)

    right_scale_dptr, right_shift_dptr, right_beta_dptr = init_line(
        param.lut_type, x_fmax, right_max)

    return out_shift_dptr, [
        sparse_table_dptr,
        dense_table_dptr,
        sparse_shift_dptr,
        sparse_scale_dptr,
        sparse_beta_dptr,
        dense_shift_dptr,
        dense_scale_dptr,
        dense_beta_dptr,
        left_shift_dptr,
        left_scale_dptr,
        left_beta_dptr,
        right_shift_dptr,
        right_scale_dptr,
        right_beta_dptr,
        sparse_min_dptr,
        sparse_max_dptr,
        dense_min_dptr,
        dense_max_dptr,
        x_min_dptr,
        x_max_dptr,
        out_shift_dptr,
    ]
