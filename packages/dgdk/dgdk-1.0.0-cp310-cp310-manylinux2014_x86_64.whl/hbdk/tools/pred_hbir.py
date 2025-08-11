from collections import OrderedDict

import sys
import numpy as np
from hbdk import hbir_helper as hbir
from hbdk.tools.pred import get_random_numpy_array


class HbirPredictor:
    def __init__(self, model_file, march):
        self.model_file = model_file
        self.march = march
        self.input_tensors = OrderedDict()
        self.hbir_model = hbir.Model()
        self.hbir_model.DeserializeFromFile(self.model_file)
        for tensor_name in list(self.hbir_model.input_tensor_names):
            tensor = self.hbir_model.Tensor(tensor_name)
            self.input_tensors[tensor.name] = tensor

    def generate_random_input(self, tensor_name):
        """Generate random inputs"""
        t = self.input_tensors[tensor_name]
        if t.dtype == 'int16':
            # int16 conv only support from -32768 to 32639(32767 - 128)
            return get_random_numpy_array(
                getattr(np, t.dtype), list(t.shape), -32768, 32639)
        return get_random_numpy_array(getattr(np, t.dtype), list(t.shape))


def main(options):
    """main of predictor for tensorflow"""
    model_file = options['model']
    assert model_file.endswith(
        '.hbir'), "Hbir model filename should ends with .hbir"
    predictor = HbirPredictor(model_file, options['march'])
    assert len(options['shape']) == len(predictor.input_tensors)\
        or len(options['shape']) == len(predictor.input_tensors) + 1, \
        "The number of shape in -s (%d)" \
        " does not match number of inputs in protobuf (%d)" % (
            len(options['shape']), len(predictor.input_tensors))

    input_index = 0
    if options['gen_random_input_and_exit']:
        for name, _ in predictor.input_tensors.items():
            a = predictor.generate_random_input(name)
            filename = options['input_binary'][input_index]
            if filename:
                a.tofile(filename)
            input_index += 1
        sys.exit(0)
    else:
        raise NotImplementedError(
            "Hbir only implements --gen-random-input-and-exit")
