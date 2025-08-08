__all__ = ['return_as_type']

import numpy as np


def return_as_type(seq, return_type=None):
    if return_type == 'scalar':
        return seq[0]
    elif return_type == 'np_arr':
        return np.array(seq)
    else:
        return seq
