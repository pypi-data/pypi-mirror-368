# pylint: skip-file

import numpy as np
import os
import re
import sys
import torch
torch.manual_seed(911)
from hbdk.tools.pred import TensorData, get_random_numpy_array, silent_remove_file
from hbdk.torch_script.utils import perm_to_native


def format_input(old_value, input_name, input_value):
    import re
    key_re = re.match(r'\[.*?\]', input_name)
    if key_re is None:
        return input_value
    key = key_re.group()[1:-1]
    if key.isdigit():
        if isinstance(old_value, list):  # list
            old_value.append(
                format_input(None, input_name[key_re.end():], input_value))
            return old_value
        elif old_value is None:
            return [input_value]
        else:
            return [
                old_value,
                format_input(None, input_name[key_re.end():], input_value)
            ]
    else:
        if old_value is None:  # dict
            return {
                key: format_input(None, input_name[key_re.end():], input_value)
            }
        elif key in old_value:
            new_value = format_input(old_value[key], input_name[key_re.end():],
                                     input_value)
            old_value[key] = new_value
            return old_value
        else:
            old_value[key] = format_input(None, input_name[key_re.end():],
                                          input_value)
            return old_value


def main(options):
    """main of predictor for torch script"""
    if options['gen_random_param_and_exit']:
        sys.exit(0)

    if options['gen_random_input_and_exit']:
        # no such function
        sys.exit(-1)

    # process input arguments
    flattened_args = []
    for name, binary, shape, dtype in zip(
            options['input_name'], options['input_binary'], options['shape'],
            options['input_dtypes']):
        data = np.fromfile(binary, dtype=np.dtype(dtype))
        data = data.reshape(shape)

        np_to_torch_dtype = {
            "int8": torch.int8,
            "int16": torch.int16,
            "int32": torch.int32,
            "float32": torch.float32
        }
        dtype = np_to_torch_dtype[dtype]

        torch_native = True
        data = torch.as_tensor(data, device='cpu', dtype=dtype).contiguous()
        if 'torch_native' not in name:
            torch_native = False
            assert len(shape) in [3, 4, 5]
            data = torch.permute(data, perm_to_native(len(shape)))

        from hbdk.torch_script.placeholder import placeholder
        ph = placeholder(
            data.size(),
            torch_native=torch_native,
            dtype=dtype,
            sample=data.contiguous())
        flattened_args.append(ph)

    # reconstruct example input
    structured_args = []
    for name_idx, name in enumerate(options['input_name']):
        input_idx_re = re.match('arg[0-9]*', name)
        if input_idx_re is None:
            raise RuntimeError("parse input name string " + name +
                               " failed. It is supposed to start with arg")
        input_idx = int(input_idx_re.group()[3:])
        if len(structured_args) == input_idx:
            new_input = format_input(None, name[input_idx_re.end():],
                                     flattened_args[name_idx])
            structured_args.append(new_input)
        elif input_idx < len(structured_args):
            structured_args[input_idx] = format_input(
                structured_args[input_idx], name[input_idx_re.end():],
                flattened_args[name_idx])

    import horizon_plugin_pytorch
    from hbdk.config import get_tool_chain_march
    horizon_plugin_pytorch.quantization.march = get_tool_chain_march(
        options['march'])

    from hbdk.torch_script.tools import trace, _preprocess_inputs
    example_inputs = _preprocess_inputs(structured_args)

    module = torch.jit.load(options['model']).eval().cpu()

    traced_module = trace(module, example_inputs)

    from hbdk.torch_script.parser import HBIRBuilder

    builder = HBIRBuilder("", options['march'], run_pred=True)
    builder.build_from_jit(traced_module, example_inputs)

    # Output files are named by following rule:
    #
    # hbdk_output_${FEATURE_NAME}.txt
    #
    # Model verifier relies on the file names and headers to compare output tensors.
    # Please modify model verifier's code correspondingly if there is any modification!
    if options['gen_txt_output']:
        os.makedirs(os.path.abspath(options["output"]), exist_ok=True)
        output_tensor_names = builder.ret_names
        for orig_output_tensor_name in output_tensor_names:
            if orig_output_tensor_name.endswith(('_dummy1_torch_native',
                                                 '_dummy2_torch_native')):
                continue
            output_tensor_name = re.split(r'\d+$', orig_output_tensor_name)[0]
            tmp_name1 = output_tensor_name + '_inhardwarelayout'
            tmp_name2 = orig_output_tensor_name + '_inhardwarelayout'
            tmp_name3 = output_tensor_name[0:output_tensor_name
                                           .rfind(':')] + '_inhardwarelayout'
            tmp_name4 = orig_output_tensor_name[
                0:orig_output_tensor_name.rfind(':')] + '_inhardwarelayout'
            tmp_name5 = orig_output_tensor_name[0:orig_output_tensor_name
                                                .rfind(':filtered:'
                                                       )] + '_inhardwarelayout'
            tmp_names = [tmp_name1, tmp_name2, tmp_name3, tmp_name4, tmp_name5]
            hardwarelayout_output_tesnor_names = []
            for name in builder.inhardware_pred_record:
                for tmp_name in tmp_names:
                    if name.find(
                            tmp_name
                    ) != -1 and name not in hardwarelayout_output_tesnor_names:
                        hardwarelayout_output_tesnor_names.append(name)
            if hardwarelayout_output_tesnor_names:
                for name in hardwarelayout_output_tesnor_names:
                    formated_tensor_name = name.replace('/', '_')
                    output_filename = os.path.join(
                        os.path.abspath(options["output"]),
                        'hbdk_output_' + formated_tensor_name + '.txt')
                    tmp_dim = int(1)
                    dtype, data = builder.inhardware_pred_record[name]
                    data = data.numpy().astype(np.dtype(dtype))
                    for dim in data.shape:
                        tmp_dim *= dim
                    tmp_dim /= data.shape[-1]
                    tmp_dim = int(tmp_dim)
                    output_reshape = data.reshape((tmp_dim, data.shape[-1]))
                    np.savetxt(output_filename, output_reshape, fmt='%.20e')
            else:
                formated_tensor_name = orig_output_tensor_name.replace(
                    '/', '_')
                output_filename = os.path.join(
                    os.path.abspath(options["output"]),
                    'hbdk_output_' + formated_tensor_name + '.txt')
                tmp_dim = int(1)

                dtype, data = builder.pred_record[orig_output_tensor_name]
                data = data.numpy().astype(np.dtype(dtype))
                for dim in data.shape:
                    tmp_dim *= dim
                tmp_dim /= data.shape[-1]
                tmp_dim = int(tmp_dim)
                output_reshape = data.reshape((tmp_dim, data.shape[-1]))
                np.savetxt(output_filename, output_reshape, fmt='%.20e')
    elif options['output']:
        silent_remove_file(options["output"])
        builder.save_pred_record(options['output'])
