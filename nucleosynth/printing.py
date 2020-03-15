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


def check_provided(variable, name):
    """Check that variable is not None
    """
    if variable is None:
        raise ValueError(f'Must provide {name}')
