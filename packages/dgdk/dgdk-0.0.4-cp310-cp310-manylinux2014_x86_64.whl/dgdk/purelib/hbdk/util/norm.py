# pylint: skip-file
r"""
Normalize arguments
"""

import re
from tempfile import NamedTemporaryFile
from typing import Tuple, AnyStr, Union, Sequence
from typing import io as tio
from .typehint import ShapeT, MxnetSymOrFileT, MxnetParamOrFileT, TfGraphOrFileT, StrOrListT
import collections
from warnings import warn
import json


def iterable_except_str_bytes(arg):
    return (isinstance(arg, collections.Iterable)
            and not isinstance(arg, (str, bytes)))


def normalize_str(s: str) -> str:
    """Normalize str: Do lower case, remove spaces, etc """
    s = s.lower()
    s = s.strip()
    s = re.sub(r'\s+', '', s)
    return s


def str_to_list(s: StrOrListT) -> Sequence[str]:
    if isinstance(s, str):
        return s.split(",")
    return s


def shape_to_str(shape: ShapeT) -> str:
    """
    normalize the shape to the one required by hbdk-cc
    :param shape: The comma separated shapes, or iterables of int (for single shape),

    :return: The comma separated NxHxWxC shapes.
    """
    if iterable_except_str_bytes(shape):
        first = next(iter(shape))
        if not iterable_except_str_bytes(first):
            if isinstance(first, str):
                s = ','.join(shape)
            else:
                s = 'x'.join([str(x) for x in shape])
        else:
            s = ','.join(['x'.join([str(x) for x in y]) for y in shape])
    else:
        s = str(shape)
    return normalize_str(s)


def shape_to_list(shape: ShapeT) -> Sequence[Sequence[int]]:
    if isinstance(shape, str):
        return [[int(val)
                 for val in s.lower().split("x")
                 if val]
                for s in shape.split(",")]
    s = []
    for x in shape:
        if isinstance(x, int):
            s.append(x)
        elif isinstance(x, str):
            s.append([int(val) for val in x.lower().split("x")])
        else:
            s.append([int(val) for val in x])
    if not iterable_except_str_bytes(next(iter(s))):
        s = [s]
    return s


def str_list_to_str(s: StrOrListT, norm: bool = True) -> str:
    """
    Normalize the input source to comma separated string
    :param s: The comma separated string, or iterables of str
    :return: The comma separated input sources
    """
    if iterable_except_str_bytes(s):
        s = ','.join(s)
    return normalize_str(s) if norm else s


def data_to_tempfile(data: AnyStr) -> tio.IO:
    if isinstance(data, str):
        data = data.encode()
    f = NamedTemporaryFile('wb')
    f.write(data)
    f.flush()
    return f


def fname_or_bin_to_file(f: Union[str, bytes]):
    if isinstance(f, str):
        return open(f, "rb")
    return data_to_tempfile(f)


def mxnet_sym_to_file(sym: MxnetSymOrFileT) -> tio.IO:
    if isinstance(sym, (str, bytes)):
        try:
            j = json.loads(sym)
            warn(
                'The text of mxnet model json has been passed to sym.'
                ' This behavior has been deprecated. Please use filename or mxnet symbol object instead',
                DeprecationWarning)
            return data_to_tempfile(sym)
        except json.JSONDecodeError:
            pass
        return open(sym, "r")
    return data_to_tempfile(sym.tojson())


def mxnet_param_to_file(sym: MxnetParamOrFileT) -> tio.IO:
    if isinstance(sym, str):
        return open(sym, "rb")
    elif isinstance(sym, bytes):
        return data_to_tempfile(sym)

    raise NotImplementedError(
        "Only supports param filename rightnow. No support for param dict")


def tf_sym_to_file(sym: TfGraphOrFileT) -> tio.IO:
    if isinstance(sym, str):
        return open(sym, "rb")
    elif isinstance(sym, bytes):
        warn(
            'The raw binary of Tensorflow GraphDef has been passed to sym.'
            ' This behavior has been deprecated. Please use filename or TF GraphDef object instead',
            DeprecationWarning)
        return data_to_tempfile(sym)
    raise NotImplementedError(
        "Only supports Tensorflow protobuf filename right now. No support for tf.GraphDef"
    )


def opt_to_str(opt: Union[str, int], factor: int = 2) -> str:

    if isinstance(opt, str):
        if opt in {'O0', 'O1', 'O2', 'O3', 'Om'}:
            return ['--' + opt]
        elif opt in {'0', '1', '2', '3', 'm'}:
            return ['--O' + opt]
        elif opt in {'fast', 'ddr'}:
            return ['--O3', '--' + opt]
        elif opt == 'balance':
            if not 0 <= factor <= 100:
                NotImplementedError(
                    "unexpected balance level : {}".format(factor))
            return ['--O3', '--balance', str(factor)]
        else:
            NotImplementedError(
                "unexpected optimization string : {}".format(opt))
    else:
        if opt in {0, 1, 2, 3}:
            return ['--O' + str(opt)]
        else:
            NotImplementedError(
                "unexpected optimization level : {}".format(opt))
