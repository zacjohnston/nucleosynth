import numpy as np

# nucleosynth
from .config import elements

"""
Functions for managing nuclear network data
"""


# ===============================================================
#                      network table
# ===============================================================
def select_network(tracer_network, a=None, z=None):
    """Return subset of tracer network with given Z and/or A

    parameters
    ----------
    tracer_network : pd.DataFrame
    z : int
    a : int
    """
    if (z is None) and (a is None):
        raise ValueError('Must specify at least one of Z, A')

    z_mask = tracer_network['Z'] == z
    a_mask = tracer_network['A'] == a

    if None in [z, a]:
        mask = np.logical_or(z_mask, a_mask)
    else:
        mask = np.logical_and(z_mask, a_mask)

    return tracer_network[mask]


# ===============================================================
#                      abu table
# ===============================================================
def select_abu(abu_table, tracer_network, z=None, a=None):
    """Return column(s) of abundance table with given Z and/or A

    parameters
    ----------
    abu_table : pd.DataFrame
    tracer_network : pd.DataFrame
    z : int
    a : int
    """
    sub_net = select_network(tracer_network, z=z, a=a)
    return abu_table.iloc[:, sub_net.index]


# ===============================================================
#                      strings
# ===============================================================
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
