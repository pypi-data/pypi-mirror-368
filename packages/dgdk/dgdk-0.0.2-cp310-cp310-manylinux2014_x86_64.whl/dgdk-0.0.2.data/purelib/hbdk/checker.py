# pylint: skip-file
"""
HBDK model checker
"""
import os
import sys
import subprocess
import tempfile

from .util.typehint import ShapeT, MxnetSymOrFileT, MxnetParamOrFileT, TfGraphOrFileT, StrOrListT
from typing import Union, Sequence
from .util.norm import shape_to_str, mxnet_sym_to_file, tf_sym_to_file, mxnet_param_to_file, \
    fname_or_bin_to_file, shape_to_list, str_to_list, str_list_to_str
from .util.process import run_program_redirect_realtime


def GenParam(model: MxnetSymOrFileT, march: str, shape: ShapeT, param_fn: str):
    """generate param for mxnet json"""
    json_fp = mxnet_sym_to_file(model)
    shape = shape_to_str(shape)
    cmd = [
        sys.executable, '-m', "hbdk.tools.pred", "--march", march, '-m',
        json_fp.name, '-s', shape, '-p', param_fn,
        '--gen-random-param-and-exit'
    ]
    p = run_program_redirect_realtime(
        cmd, stdout=sys.stdout, stderr=sys.stderr)
    ret = p.returncode
    if ret != 0:
        print("HBDK generate random param error, please check with HBDK Group")
    json_fp.close()
    return p.returncode


gen_param = GenParam  # GenParam does not follow PEP8


def _run_model_check_with_cmd(cmd: Sequence[str]):
    p = run_program_redirect_realtime(
        cmd, stdout=sys.stdout, stderr=sys.stderr)
    ret = p.returncode
    if ret != 0:
        print("HBDK model check FAIL, please check with HBDK Group")
    else:
        print("HBDK model check PASS")
    return ret


def CheckMxnetModel(model: MxnetSymOrFileT,
                    march: str,
                    shape: ShapeT,
                    input_name: StrOrListT = None,
                    input_source: StrOrListT = None,
                    param: MxnetParamOrFileT = None,
                    advice: int = 0,
                    check_quanti_param: bool = True):
    """
    check mxnet model
    :param model: path to the json model filename, or the mxnet symbol object
    :param march: Target BPU micro architecture.
                  Supported march: bernoulli, bernoulli2, bayes (dev use only).
    :param shape: NHWC shape for input features. Can be list of ints, comma separated string.
    :param input_name: Specify input features' names.
                    Can be list of string, or comma separated string
    :param input_source: Specify input features' sources(ddr/resizer/pyramid),
                         Can be list of string, or comma separated string
    :param param:  mxnet parameters filename, or dictionary of ndarray.
    :param advice: Print advice if a layer is slowed down by more than the
                   specified time (in microseconds).
    :param check_quanti_param: Check quanti param
    :return: 0 if model check pass.
    """

    json_fp = mxnet_sym_to_file(model)
    shape = shape_to_str(shape)
    if param:
        param_fp = mxnet_param_to_file(param)
    else:
        param_fp = tempfile.NamedTemporaryFile("wb")
        ret = gen_param(model, march, shape, param_fp.name)
        if ret != 0:
            return ret

    cmd = [
        'hbdk-model-check', '--march', march, '-m', json_fp.name, '-s', shape,
        '-p', param_fp.name, '-f', 'mxnet'
    ]
    if input_source:
        input_source = str_list_to_str(input_source)
        cmd += ['-i', input_source]
    if input_name:
        input_name = str_list_to_str(input_name)
        cmd += ['--input-name', input_name]
    if advice:
        cmd += ['--advice', str(advice)]
    if not check_quanti_param:
        cmd += ['--skip-check-quanti-param']
    ret = _run_model_check_with_cmd(cmd)
    json_fp.close()
    param_fp.close()
    return ret


check_mxnet_model = CheckMxnetModel


def CheckHbirModel(model: str,
                   march: str,
                   input_name: StrOrListT = None,
                   input_source: StrOrListT = None,
                   advice: int = 0,
                   check_quanti_param: bool = True):
    """
    check hbir model
    :param model: hbir data (.hbir)
    :param march: Target BPU micro architecture.
                  Supported march: bernoulli, bernoulli2, bayes (dev use only).
    :param input_name: Specify input features' names.
                    Can be list of string, or comma separated string
    :param input_source: Specify input features' sources(ddr/resizer/pyramid),
                    Can be list of string, or comma separated string
    :param advice: Print advice if a layer is slowed down by more than the
                   specified time (in microseconds).
    :param check_quanti_param: Check quanti param
    :return: 0 if model check pass.
    """

    hbir_fp = fname_or_bin_to_file(model)

    cmd = [
        'hbdk-model-check', '--march', march, '-m', hbir_fp.name, '-f', 'hbir'
    ]
    hbir_fp.close()
    if input_source:
        input_source = str_list_to_str(input_source)
        cmd += ['-i', input_source]
    if input_name:
        input_name = str_list_to_str(input_name)
        cmd += ['--input-name', input_name]
    if advice:
        cmd += ['--advice', str(advice)]
    if not check_quanti_param:
        cmd += ['--skip-check-quanti-param']
    ret = _run_model_check_with_cmd(cmd)
    return ret


check_hbir_model = CheckHbirModel


def CheckTensorflowModel(model: TfGraphOrFileT,
                         march: str,
                         shape: ShapeT,
                         input_name: StrOrListT = None,
                         input_source: StrOrListT = None,
                         output_nodes: StrOrListT = None,
                         advice: int = 0,
                         check_quanti_param: bool = True):
    """
    check tensorflow model
    :param model: tensorflow model data (.pb)
    :param march: Target BPU micro architecture.
                  Supported march: bernoulli, bernoulli2, bayes (dev use only).
    :param shape: NHWC shape for input features, separated by comma
    :param input_name: Specify input features' names.
                    Can be list of string, or comma separated string
    :param input_source: Specify input features' sources(ddr/resizer/pyramid),
                    Can be list of string, or comma separated string
    :param output_nodes: List of model output names, or comma separated string.
    :param advice: Print advice if a layer is slowed down by more than the
                   specified time (in microseconds).
    :param check_quanti_param: Check quanti param
    :return: 0 if model check pass.
    """

    tf_fp = tf_sym_to_file(model)
    shape = shape_to_str(shape)
    input_source = str_list_to_str(input_source)

    cmd = [
        'hbdk-model-check', '--march', march, '-m', tf_fp.name, '-s', shape,
        '-f', 'tf'
    ]
    if input_source:
        input_source = str_list_to_str(input_source)
        cmd += ['-i', input_source]
    if input_name:
        input_name = str_list_to_str(input_name)
        cmd += ['--input-name', input_name]
    if output_nodes:
        cmd += ['--tf-output-node-names', str_list_to_str(output_nodes, False)]
    if advice:
        cmd += ['--advice', str(advice)]
    if not check_quanti_param:
        cmd += ['--skip-check-quanti-param']
    ret = _run_model_check_with_cmd(cmd)
    tf_fp.close()
    return ret


check_tensorflow_model = CheckTensorflowModel
