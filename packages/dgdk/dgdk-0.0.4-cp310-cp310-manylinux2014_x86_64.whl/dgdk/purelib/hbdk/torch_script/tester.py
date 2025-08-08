import pickle
import torch


def run_test(module, example_inputs):
    """
    run integration test on the input pytorch module.
    """

    import argparse

    parser = argparse.ArgumentParser(description='Generate a torch script')
    parser.add_argument('march', help='Target BPU micro architecture')
    parser.add_argument('pt', help='path to export torchscript')
    parser.add_argument('hbir', help='path to export hbir')
    parser.add_argument('pred', help='path to export pred reference')
    parser.add_argument('bin', help='directory to export input binaries')
    parser.add_argument(
        'bin_paths', help='path to export input binaries file paths')
    parser.add_argument('names', help='path to export input tensor names')
    args = parser.parse_args()

    import horizon_plugin_pytorch
    from hbdk.config import get_tool_chain_march, March, get_normalized_march

    horizon_plugin_pytorch.quantization.march = get_tool_chain_march(
        args.march)

    from hbdk.torch_script.tools import trace, _preprocess_inputs

    # save example_inputs for post_check
    with open(args.bin + "/placeholder_info.pickle", "wb") as f:
        pickle.dump(example_inputs, f)

    example_inputs = _preprocess_inputs(example_inputs)

    traced_module = trace(module, example_inputs)
    torch.jit.save(traced_module, args.pt)

    from hbdk.torch_script.parser import HBIRBuilder
    builder = HBIRBuilder("", args.march, True)
    builder.build_from_jit(traced_module, example_inputs)

    builder.save_pred_record(args.pred)
    builder.save_input(args.bin)

    # save input binary file path for cc, sim, verify
    bin_files = []
    for name in builder.arg_names:
        bin_files.append("%s/%s.bin" % (args.bin, name))
    with open(args.bin_paths, 'w') as f:
        f.write(','.join(bin_files))

    # save input names for cc
    with open(args.names, 'w') as f:
        f.write(','.join(builder.arg_names))

    builder.hbir_model.SerializeToFile(args.hbir)
