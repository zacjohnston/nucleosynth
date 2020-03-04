"""
Module for formatting/printing strings
"""


def printv(string, verbose, **kwargs):
    """Print string if verbose is True

    parameters
    ----------
    string : str
    verbose : bool
    """
    if verbose:
        print(string, **kwargs)
