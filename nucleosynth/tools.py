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


def expand_sequence(x, start_from=0):
    """If x is int, return (np.arange(x) + start_from), else return x

    parameters
    ----------
    x : int or 1D-array
    start_from : int
    """
    if isinstance(x, (list, tuple, np.ndarray)):
        return x
    else:
        return np.arange(x) + start_from
