import argparse
import torch
import horizon_plugin_pytorch  # pylint: disable=unused-import
from hbdk.torch_script.tools import export_hbir


def main():

    parser = argparse.ArgumentParser(
        description='Convert torch script file to hbir')
    parser.add_argument(
        '-i', '--input', required=True, help='path to torch script file')
    parser.add_argument('--march', required=True, help='specify march')
    parser.add_argument(
        '-s',
        '--shape',
        required=False,
        help='NHWC shape for input features, separate by comma')
    parser.add_argument(
        '--example-input',
        required=False,
        help='Specify example input generation file')
    parser.add_argument(
        '-o', '--output', required=True, help='path to output hbir file')
    args = parser.parse_args()

    ts = torch.jit.load(args.input)

    example_inputs = []
    if args.example_input:
        ei_file = args.example_input.split('.')
        assert len(ei_file) == 2
        assert ei_file[1] == 'py'

        import importlib
        mod = importlib.import_module(ei_file[0])
        example_inputs = mod.example_inputs
    else:
        input_shapes = []
        for shape in args.shape.strip().lower().split(','):
            input_shapes.append([int(x) for x in shape.split('x')])

        def _shape_nhwc_to_nchw(shape):
            return [shape[0], shape[-1], *shape[1:-1]]

        nchw_shapes = []
        for shape in input_shapes:
            nchw_shapes.append(_shape_nhwc_to_nchw(shape))

        ts.eval().cpu()
        for s in nchw_shapes:
            example_inputs.append(torch.Tensor(*s, device='cpu'))
    export_hbir(ts, example_inputs, args.output, args.march)


if __name__ == "__main__":
    main()
