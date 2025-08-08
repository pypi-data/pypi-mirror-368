import os
import torch
from typing import Union, Sequence
from hbdk.torch_script.placeholder import placeholder


def _norm_march(march):
    if march is None:
        # if not set, use plugin global march
        import horizon_plugin_pytorch
        return horizon_plugin_pytorch.march.get_march()
    return march


def _preprocess_inputs(example_inputs):
    def dfs(x):
        if isinstance(x, (list, tuple)):
            return [dfs(i) for i in x]
        if isinstance(x, dict):
            return {k: dfs(x[k]) for k in sorted(x.keys())}
        if isinstance(x, torch.Tensor):
            if len(x.size()) in [3, 4, 5]:
                torch_native = False
            else:
                torch_native = True
            return placeholder(
                x.size(), torch_native=torch_native, dtype=x.dtype,
                sample=x)  # align to legacy behavior
        return x

    return dfs(example_inputs)


def trace(obj, placeholders):
    """call torch.jit.trace with placeholders.

    Parameters
    ----------
      module: nn.Module or jit.ScriptModule.
      placeholders: A tuple of example inputs wrapped by hbdk.torch_script.placeholder.
      hbir: Specify the output path of hbir.

    Returns
    -------
    flag: int
      0 if pass, otherwise not.
    """

    def dfs(x):
        if isinstance(x, list):
            return [dfs(i) for i in x]
        if isinstance(x, tuple):
            return tuple([dfs(i) for i in x])
        if isinstance(x, dict):
            return {k: dfs(x[k]) for k in sorted(x.keys())}
        if isinstance(x, placeholder):
            if x.sample is None:
                return torch.randn(x.shape, dtype=x.dtype)
            return x.sample
        return x

    placeholders = dfs(placeholders)
    return torch.jit.trace(obj, placeholders)


def _trace_module(module, example_inputs):
    module.eval()
    if isinstance(module, torch.jit.ScriptModule):
        return module

    try:
        traced_module = trace(module, example_inputs)
        return traced_module
    except (Exception):
        raise RuntimeError(
            "torch.jit.trace fail. Please make sure the model is traceable.")


def export_hbir(module: Union[torch.jit.ScriptModule, torch.nn.Module],
                example_inputs: tuple,
                hbir: str,
                march: str = None):
    """Export the nn.Module or jit.ScriptModule to hbdk3.HBIR.

    Parameters
    ----------
      module: nn.Module or jit.ScriptModule.
      example_inputs: A tuple of example inputs, in torch.tensor format.
                      For jit.trace and shape inference.
      hbir: Specify the output path of hbir.
      march: Specify march to export hbir.
             Valid options are bayes and bernoulli2.
             If not provided, use horizon plugin global march.

    Returns
    -------
    input names and output names
    """
    from hbdk.torch_script.parser import HBIRBuilder
    traced_module = _trace_module(module, example_inputs)
    if not hbir.endswith(".hbir"):
        print('argument "hbir" must end with .hbir')
        return 1
    example_inputs = _preprocess_inputs(example_inputs)

    pt = hbir.replace(".hbir", ".pt")
    torch.jit.save(traced_module, pt)
    script_module = torch.jit.load(pt)

    march = _norm_march(march)
    builder = HBIRBuilder("", march)
    builder.build_from_jit(script_module, example_inputs)

    if len(builder.arg_names) != 1:
        print("WARNING: model has multiple input tensors that are",
              tuple(builder.arg_names))

    if len(builder.ret_names) != 1:
        print("WARNING: model has multiple output tensors that are",
              tuple(builder.ret_names))

    arg_names = builder.arg_names
    ret_names = builder.ret_names
    builder.hbir_model.SerializeToFile(hbir)
    return arg_names, ret_names


def check_model(
        module: Union[torch.jit.ScriptModule, torch.nn.Module],
        example_inputs: tuple,
        march: str = None,
        input_source: Union[Sequence[str], str] = "ddr",
        advice: int = None,
        check_quanti_param: bool = True,
):
    """
    Check if nn.Module or jit.ScriptModule can be compiled by HBDK.
         Dump advices for improving performance on BPU.

    Parameters
    ----------
      module: nn.Module or jit.ScriptModule.
      example_inputs: A tuple of example inputs, in torch.tensor format.
                      For jit.trace and shape inference.
      march: Specify the target march of bpu.
             Valid options are bayes and bernoulli2.
             If not provided, use horizon plugin global march.
      input_source: Specify input features' sources(ddr/resizer/pyramid).
      advice: Print HBDK compiler advices for improving the utilization of the
              model on bpu if layers of the model become slow by more than the
              specified time (in microseconds)
      check_quanti_param: Check quanti param

    Returns
    -------
    flag: int
      0 if pass, otherwise not.
    """
    march = _norm_march(march)
    from tempfile import NamedTemporaryFile
    hbir_file = NamedTemporaryFile(suffix=".hbir", delete=True)
    export_hbir(module, example_inputs, hbir_file.name, march)

    from ..checker import check_hbir_model

    return check_hbir_model(
        hbir_file.name,
        march=march,
        input_source=input_source,
        advice=advice,
        check_quanti_param=check_quanti_param)


def compile_model(
        module: Union[torch.jit.ScriptModule, torch.nn.Module],
        example_inputs: tuple,
        hbm: str,
        march: str = None,
        name: str = None,
        input_source: Union[Sequence[str], str] = "ddr",
        input_layout: str = None,
        output_layout: str = "NCHW",
        opt: Union[str, int] = "O2",
        balance_factor: int = 2,
        progressbar: bool = True,
        jobs: int = 16,
        debug: bool = True,
        extra_args: list = None,
):
    """Compile the nn.Module or jit.ScriptModule.

    Parameters
    ----------
      module: nn.Module or jit.ScriptModule.
      example_inputs: A tuple of example inputs, in torch.tensor format.
                      For jit.trace and shape inference.
      hbm: Specify the output path of hbdk-cc.
      march: Specify the target march of bpu.
             Valid options are bayes and bernoulli2.
             If not provided, use horizon plugin global march.
      name: Name of the model, recorded in hbm.
            Can be obtained by hbdk-disas or hbrtGetModelNamesInHBM in runtime.
      input_source: Specify input features' sources(ddr/resizer/pyramid).
      input_layout: Specify input layout of all model inputs.
                    Available layouts are NHWC, NCHW, BPU_RAW.
      output_layout: Specify input layout of all model inputs.
                     Available layouts are NHWC, NCHW, BPU_RAW.
      opt: Specify optimization options.
           Available options are O0, O1, O2, O3, ddr, fast, balance.
      balance_factor: Specify the balance ratio when optimization options is
                      'balance'.
      progressbar: Show compilation progress to alleviate anxiety.
      jobs: Specify number of threads launched during compiler optimization.
            Default is '16'. 0 means use all available hardware concurrency.
      debug: Enable debugging info in hbm.
      extra_args: specify extra args listed in "hbdk-cc -h".
                  format in list of string:
                  e.g. ['--ability-entry', str(entry_value), ...]

    Returns
    -------
    flag: int
      0 if pass, otherwise not.
    """

    march = _norm_march(march)

    from tempfile import NamedTemporaryFile

    traced_module = _trace_module(module, example_inputs)

    if not hbm.endswith(".hbm"):
        print('argument "hbm" must end with .hbm')
        return 1

    hbir_file = NamedTemporaryFile(suffix=".hbir", delete=True)

    hbir_file_path = hbir_file.name
    # if hbm is not temporary file then export hbir in hbm path
    if not hbm.startswith("hbdktmp_"):
        hbir_file_path = hbm[:-4] + ".hbir"

    hbir_input_names, hbir_output_names = export_hbir(module, example_inputs,
                                                      hbir_file_path, march)

    if not name:
        name = traced_module.original_name

    from ..compiler import compile_hbir_model

    return compile_hbir_model(
        model=hbir_file_path,
        march=march,
        input_name=hbir_input_names,
        input_source=input_source,
        hbm=hbm,
        name=name,
        input_layout=input_layout,
        output_layout=output_layout,
        opt=opt,
        balance_factor=balance_factor,
        progressbar=progressbar,
        visualize=False,
        jobs=jobs,
        debug=debug,
        extra_args=extra_args,
    )


def perf_hbm(hbm: str, out_dir: str, layer_details: bool = False):
    """Estimate the performance of the given hbm.

    Parameters
    ----------
      hbm: Specify the path to hbm.
      out_dir: Specify the output directry to hold the performance results.
      layer_details: show layer performance details. (dev use only)

    Returns
    -------
    flag: int
      0 if pass, otherwise not.
    """

    cmd = ["hbdk-perf", hbm, "-o", out_dir]

    if layer_details:
        cmd += ["--internal-detail"]

    from ..compiler import _run_model_compile_with_cmd
    ret = _run_model_compile_with_cmd(cmd)
    if ret != 0:
        raise RuntimeError(
            "HBDK performance estimation FAIL, please check with HBDK Group")
    else:
        print("HBDK performance estimation SUCCESS")
    return ret


def perf_model(
        module: Union[torch.jit.ScriptModule, torch.nn.Module],
        example_inputs: tuple,
        march: str = None,
        out_dir: str = ".",
        name: str = None,
        hbm: str = None,
        input_source: Union[Sequence[str], str] = "ddr",
        input_layout: str = None,
        output_layout: str = "NCHW",
        opt: Union[str, int] = "O3",
        balance_factor: int = 2,
        progressbar: bool = True,
        jobs: int = 16,
        layer_details: bool = False,
        extra_args: list = None,
):
    """Estimate the performance of nn.Module or jit.ScriptModule.

    Parameters
    ----------
      module: nn.Module or jit.ScriptModule.
      example_inputs: A tuple of example inputs, in torch.tensor format.
                      For jit.trace and shape inference.
      march: Specify the target march of bpu.
             Valid options are bayes and bernoulli2.
             If not provided, use horizon plugin global march.
      out_dir: Specify the output directry to hold the performance results.
      name: Name of the model, recorded in hbm.
            Can be obtained by hbdk-disas or hbrtGetModelNamesInHBM in runtime.
      hbm: Specify the output path of hbdk-cc.
      input_source: Specify input features' sources(ddr/resizer/pyramid).
      input_layout: Specify input layout of all model inputs.
                    Available layouts are NHWC, NCHW, BPU_RAW.
      output_layout: Specify input layout of all model inputs.
                     Available layouts are NHWC, NCHW, BPU_RAW.
      opt: Specify optimization options.
           Available options are O0, O1, O2, O3, ddr, fast, balance.
      balance_factor: Specify the balance ratio when optimization options is
                      'balance'.
      progressbar: Show compilation progress to alleviate anxiety.
      jobs: Specify number of threads launched during compiler optimization.
            Default is '16'. 0 means use all available hardware concurrency.
      layer_details: show layer performance details. (dev use only)
      extra_args: specify extra args listed in "hbdk-cc -h".
                  format in list of string:
                  e.g. ['--ability-entry', str(entry_value), ...]

    Returns
    -------
      Performance details in json dict. Or error code when fail.
    """

    from tempfile import NamedTemporaryFile

    hbm_file = NamedTemporaryFile(
        prefix="hbdktmp_", suffix=".hbm", delete=True)
    if not hbm:
        hbm = hbm_file.name

    traced_module = _trace_module(module, example_inputs)

    if not name:
        name = traced_module.original_name

    ret = compile_model(
        module=traced_module,
        example_inputs=example_inputs,
        march=march,
        input_source=input_source,
        hbm=hbm,
        name=name,
        input_layout=input_layout,
        output_layout=output_layout,
        opt=opt,
        balance_factor=balance_factor,
        progressbar=progressbar,
        jobs=jobs,
        debug=True,
        extra_args=extra_args,
    )
    if ret != 0:
        return ret

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    ret = perf_hbm(hbm=hbm, out_dir=out_dir, layer_details=layer_details)
    if ret != 0:
        return ret

    import json

    with open(out_dir + "/" + name + ".json", "rb") as f:
        return json.load(f)


def visualize_model(
        module: Union[torch.jit.ScriptModule, torch.nn.Module],
        example_inputs: tuple,
        march: str = None,
        save_path: str = None,
        show: bool = True,
):
    """Visualize nn.Module or jit.ScriptModule at the view of HBDK.

    Parameters
    ----------
      module: nn.Module or jit.ScriptModule.
      example_inputs: A tuple of example inputs, in torch.tensor format.
                      For jit.trace and shape inference.
      march: Specify the target march of bpu.
             Valid options are bayes and bernoulli2.
             If not provided, use horizon plugin global march.
      save_path: Specify path to save the plot image.
      show: Display the plotted image via display.
            Make sure X-server is correctly configured.

    Returns
    -------
      None
    """

    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmpdir:
        hbm_file_name = tmpdir + '/model.hbm'

        ret = compile_model(
            module,
            example_inputs,
            march=march,
            input_source="ddr",
            hbm=hbm_file_name,
            name=None,
            input_layout=None,
            output_layout="NCHW",
            opt="O0",
            progressbar=False,
            jobs=1,
            extra_args=["--dev-dump-graph"])
        if ret != 0:
            raise RuntimeError("visualize model via hbdk-cc failed!")

        if not save_path:
            save_path = tmpdir + '/graph.svg'
            img_type = "svg"
        else:
            img_type = save_path.split(".")[-1]

        import sys
        import subprocess

        cmd = [
            "dot",
            "-T",
            img_type,
            os.path.dirname(hbm_file_name) + "/000_original.dot",
            "-o",
            save_path,
        ]
        p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
        ret = p.wait()
        if ret != 0:
            raise RuntimeError("Dot plot failed")

        if show:
            cmd = ["firefox", save_path]
            p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
            p.wait()
