import numpy as np

"""
Misc. convenience functions
"""


def ensure_sequence(x):
    """Ensure given object is in the form of a sequence.
    If object is scalar, return as length-1 list.

    parameters
    ----------
    x : 1D-array or scalar
    """
    if isinstance(x, (list, tuple, np.ndarray)):
        return x
    else:
        return [x, ]


def expand_sequence(x):
    """If x is an int, return np.arange(x), else return x

    parameters
    ----------
    x : int or 1D-array
    """
    if isinstance(x, (list, tuple, np.ndarray)):
        return x
    else:
        return np.arange(x)