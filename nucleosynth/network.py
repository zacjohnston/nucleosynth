# nucleosynth
from . import load_save
from .config import elements

"""
Functions for managing nuclear network data
"""


def get_tracer_network(tracer, model):
    """Load isotope info (Z, A) from tracer

    parameters
    ----------
    tracer : int
    model : str
    """
    net = load_save.load_tracer_network(tracer, model)
    iso_list = []

    for i in range(len(net)):
        row = net.loc[i]
        iso_str = get_isotope_str(z=row['Z'], a=row['A'])
        iso_list += [iso_str]

    net['isotope'] = iso_list
    return net[['isotope', 'Z', 'A']]


def get_isotope_str(z, a):
    """Return string for given isotope

    parameters
    ----------
    z : int
        atomic number
    a : int
        atomic mass
    """
    if a < 1 or z < 0:
        raise ValueError('Invalid isotope')

    element = get_element_str(z)

    if z == 0:  # special case for neutrons
        if a == 1:
            return element
        else:
            raise ValueError('Invalid isotope')
    else:
        return f'{element}{a}'


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
