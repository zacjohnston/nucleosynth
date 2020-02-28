# nucleosynth
from . import load_save
from .config import elements

"""
Functions for managing nuclear network data
"""


def get_network(tracer, model):
    """Load isotope info (Z, A) from tracer

    parameters
    ----------
    tracer : int
    model : str
    """
    return load_save.load_network(tracer, model)


def get_element_str(z):
    """Return string for given element

    parameters
    ----------
    z : int
        atomic number
    """
    names = elements.elements
    if z in names:
        return names[z]
    else:
        raise ValueError(f'element with Z={z} not defined. Check config/elements.py')
