import torch

from hbdk.torch_script.utils import hbir_base, TensorManager


class placeholder(object):
    def __init__(self,
                 *shape,
                 dtype=torch.float32,
                 torch_native=False,
                 sample=None):
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            self.shape = shape[0]
        else:
            self.shape = shape

        self.dtype = dtype
        self.torch_native = torch_native
        self.sample = sample

    def __repr__(self):
        return "Placeholder(size=%s, dtype=%s, torch_native=%s)" % ("x".join(
            str(x) for x in self.shape), self.dtype, self.torch_native)

    def tensor_manager(self, name):
        """
        morph placeholder to tensor manager with empty hbir inside.
        :param name: name of hbir.tensor
        :return: tensor manager object
        """
        shape = self.shape
        if self.torch_native:
            name += '_torch_native'
        else:
            if len(shape) >= 3:
                shape = [self.shape[0], *shape[2:], shape[1]]

        float_map = {torch.float32: 'float32'}
        int_map = {
            torch.int8: 'int8',
            torch.int16: 'int16',
            torch.int32: 'int32',
            torch.int64: 'int32'
        }
        if self.dtype in float_map.keys():
            hbir = hbir_base.CreateTensorf(name, shape, float_map[self.dtype],
                                           [], [], [])
        else:
            hbir = hbir_base.CreateTensor(name, shape, int_map[self.dtype], [],
                                          [], [])

        return TensorManager(hbir, self.torch_native, self.sample)
