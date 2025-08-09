# pylint: skip-file
"""
HBDK compiler
"""
import os
import sys
import subprocess

from .util.typehint import ShapeT, MxnetSymOrFileT, MxnetParamOrFileT, TfGraphOrFileT, StrOrListT
from typing import Union, Sequence
from .util.norm import shape_to_str, mxnet_sym_to_file, tf_sym_to_file, mxnet_param_to_file, \
    fname_or_bin_to_file, str_list_to_str, opt_to_str

from hbdk.util.process import run_program_redirect_realtime


def _run_model_compile_with_cmd(cmd: Sequence[str]):
    p = run_program_redirect_realtime(
        cmd, stdout=sys.stdout, stderr=sys.stderr)
    ret = p.returncode
    if ret != 0:
        raise RuntimeError(
            "HBDK model compilation FAIL, please check with HBDK Group")
    else:
        print("HBDK model compilation SUCCESS")
    return ret


def CompileMxnetModel(model: MxnetSymOrFileT,
                      march: str,
                      shape: ShapeT,
                      param: MxnetParamOrFileT,
                      hbm: str,
                      input_name: StrOrListT = None,
                      input_source: StrOrListT = None,
                      name: str = None,
                      input_layout: str = None,
                      output_layout: str = None,
                      opt: Union[str, int] = 'O2',
                      balance_factor: int = 2,
                      progressbar: bool = True,
                      visualize: bool = False,
                      debug: bool = False,
                      jobs: int = 16,
                      extra_args: list = None):
    """
    compile mxnet model
    :param model: path to the json model filename, or the mxnet symbol object
    :param march: Target BPU micro architecture.
                  Supported march: bernoulli, bernoulli2, bayes (dev use only)
    :param shape: NHWC shape for input features. Can be list of ints, comma separated string.
    :param param:  mxnet parameters filename, or dictionary of ndarray
    :param hbm: Output hbm filename.
    :param input_name: Specify input features' names.
                    Can be list of string, or comma separated string
    :param input_source: Specify input features' sources(ddr/resizer/pyramid),
                    Can be list of string, or comma separated string
    :param name: Name of the model.
                 Recorded in hbm, can be retrieved by hbdk-disas or hbrtGetModelNamesInHBM in runtime.
    :param input_layout: Specify input layout of all model inputs.
                         Available layouts are NHWC, NCHW, BPU_RAW.
    :param output_layout: Specify output layout of all modle outputs.
                         Available layouts are NHWC, NCHW, BPU_RAW.
    :param opt: Specify optimization options.
                Available options are O0, O1, O2, O3, ddr, fast, balance.
    :param balance_factor: Specify the balance ratio when optimization options is 'balance'.
    :param progressbar: Show compilation progress to alleviate anxiety.
    :param visualize: Visualize graph of compiler ir. Internal use only.
    :param jobs: Specify number of threads launched during compiler optimization.
                 Default is '16'. 0 means use all available hardware concurrency.
    :param debug: Enable debugging info in hbm.
    :param extra_args: specify extra args listed in "hbdk-cc -h".

    :return: 0 if model compile pass
    """

    json_fp = mxnet_sym_to_file(model)
    shape = shape_to_str(shape)
    param_fp = mxnet_param_to_file(param)

    cmd = [
        'hbdk-cc', '--march', march, '-m', json_fp.name, '-s', shape, '-p',
        param_fp.name, '-f', 'mxnet', *opt_to_str(opt, balance_factor), '-o',
        hbm, '--jobs',
        str(jobs)
    ]
    if name:
        cmd += ['-n', name]
    if input_source:
        input_source = str_list_to_str(input_source)
        cmd += ['-i', input_source]
    if input_name:
        input_name = str_list_to_str(input_name)
        cmd += ['--input-name', input_name]
    if input_layout:
        cmd += ['--input-layout', input_layout]
    if output_layout:
        cmd += ['--output-layout', output_layout]
    if progressbar:
        cmd += ['--progressbar']
    if visualize:
        cmd += ['--dev-dump-graph']
    if debug:
        cmd += ['--debug']
    if extra_args:
        cmd += extra_args

    ret = _run_model_compile_with_cmd(cmd)
    json_fp.close()
    param_fp.close()
    return ret


compile_mxnet_model = CompileMxnetModel


def CompileHbirModel(model: str,
                     march: str,
                     hbm: str,
                     input_name: StrOrListT = None,
                     input_source: StrOrListT = None,
                     name: str = None,
                     input_layout: str = None,
                     output_layout: str = None,
                     opt: Union[str, int] = 'O2',
                     balance_factor: int = 2,
                     progressbar: bool = True,
                     visualize: bool = False,
                     debug: bool = False,
                     jobs: int = 16,
                     extra_args: list = None):
    """
    compile hbir model
    :param model: hbir data (.hbir)
    :param march: Target BPU micro architecture.
                  Supported march: bernoulli, bernoulli2, bayes (dev use only)
    :param hbm: Output hbm filename.
    :param input_name: Specify input features' names.
                    Can be list of string, or comma separated string.
    :param input_source: Specify input features' sources(ddr/resizer/pyramid),
                         Can be list of string, separated by comma.
    :param name: Name of the model.
                 Recorded in hbm, can be retrieved by hbdk-disas or hbrtGetModelNamesInHBM in runtime.
    :param input_layout: specify input layout of all model inputs.
                         Available layouts are NHWC, NCHW, BPU_RAW.
    :param output_layout: specify output layout of all modle outputs.
                         Available layouts are NHWC, NCHW, BPU_RAW.
    :param opt: specify optimization options.
                Available options are O0, O1, O2, O3, ddr, fast, balance.
    :param balance_factor: specify the balance ratio when optimization options is 'balance'.
    :param progressbar: show compilation progress to alleviate anxiety.
    :param visualize: Visualize graph of compiler ir. Internal use only.
    :param jobs: specify number of threads launched during compiler optimization.
                 Default is '16'. 0 means use all available hardware concurrency.
    :param debug: Enable debugging info in hbm.
    :param extra_args: specify extra args listed in "hbdk-cc -h".

    :return: 0 if model compile pass
    """

    hbir_fp = fname_or_bin_to_file(model)

    cmd = [
        'hbdk-cc', '--march', march, '-m', hbir_fp.name, '-f', 'hbir',
        *opt_to_str(opt, balance_factor), '-o', hbm, '--jobs',
        str(jobs)
    ]
    if name:
        cmd += ['-n', name]
    if input_source:
        input_source = str_list_to_str(input_source)
        cmd += ['-i', input_source]
    if input_name:
        input_name = str_list_to_str(input_name)
        cmd += ['--input-name', input_name]
    if input_layout:
        cmd += ['--input-layout', input_layout]
    if output_layout:
        cmd += ['--output-layout', output_layout]
    if progressbar:
        cmd += ['--progressbar']
    if visualize:
        cmd += ['--dev-dump-graph']
    if debug:
        cmd += ['--debug']
    if extra_args:
        cmd += extra_args
    ret = _run_model_compile_with_cmd(cmd)
    hbir_fp.close()
    return ret


compile_hbir_model = CompileHbirModel


def CompileTensorflowModel(model: TfGraphOrFileT,
                           march: str,
                           shape: ShapeT,
                           hbm: str,
                           input_name: StrOrListT = None,
                           input_source: StrOrListT = None,
                           name: str = None,
                           output_nodes: StrOrListT = None,
                           input_layout: str = None,
                           output_layout: str = None,
                           opt: Union[str, int] = 'O2',
                           balance_factor: int = 2,
                           progressbar: bool = True,
                           visualize: bool = False,
                           debug: bool = False,
                           jobs: int = 16,
                           extra_args: list = None):
    """
    check tensorflow model
    :param model: tensorflow model data (.pb)
    :param march: Target BPU micro architecture.
                  Supported march: bernoulli, bernoulli2, bayes (dev use only)
    :param shape: NHWC shape for input features, separated by comma.
    :param hbm: Output hbm filename.
    :param input_name: Specify input features' names.
                    Can be list of string, or comma separated string.
    :param input_source: Specify input features' sources(ddr/resizer/pyramid),
                         separated by comma.
    :param output_nodes: List of model output names, or comma separated string.
    :param name: Name of the model.
                 Recorded in hbm, can be retrieved by hbdk-disas or hbrtGetModelNamesInHBM in runtime.
    :param input_layout: specify input layout of all model inputs.
                         Available layouts are NHWC, NCHW, BPU_RAW.
    :param output_layout: specify output layout of all modle outputs.
                         Available layouts are NHWC, NCHW, BPU_RAW.
    :param opt: specify optimization options.
                Available options are O0, O1, O2, O3, ddr, fast, balance.
    :param balance_factor: specify the balance ratio when optimization options is 'balance'.
    :param progressbar: show compilation progress to alleviate anxiety.
    :param visualize: Visualize graph of compiler ir. Internal use only.
    :param jobs: specify number of threads launched during compiler optimization.
                 Default is '16'. 0 means use all available hardware concurrency.
    :param debug: Enable debugging info in hbm.
    :param extra_args: specify extra args listed in "hbdk-cc -h".

    :return: 0 if model compile pass
    """

    tf_fp = tf_sym_to_file(model)
    shape = shape_to_str(shape)
    output_nodes = str_list_to_str(output_nodes, False)

    cmd = [
        'hbdk-cc', '--march', march, '-m', tf_fp.name, '-s', shape, '-f', 'tf',
        *opt_to_str(opt, balance_factor), '-o', hbm, '--jobs',
        str(jobs)
    ]
    if name:
        cmd += ['-n', name]
    if input_source:
        input_source = str_list_to_str(input_source)
        cmd += ['-i', input_source]
    if input_name:
        input_name = str_list_to_str(input_name)
        cmd += ['--input-name', input_name]
    if input_layout:
        cmd += ['--input-layout', input_layout]
    if output_layout:
        cmd += ['--output-layout', output_layout]
    if output_nodes:
        cmd += ['--tf-output-node-names', output_nodes]
    if progressbar:
        cmd += ['--progressbar']
    if visualize:
        cmd += ['--dev-dump-graph']
    if debug:
        cmd += ['--debug']
    if extra_args:
        cmd += extra_args

    ret = _run_model_compile_with_cmd(cmd)
    tf_fp.close()
    return ret


compile_tensorflow_model = CompileTensorflowModel
