# nucleosynth
from .config import elements

"""
Functions for managing nuclear network data
"""


# ===============================================================
#                      network table
# ===============================================================
def select_a(tracer_network, a):
    """Return subset of tracer network with given A (atomic mass number)
    """
    mask = tracer_network['A'] == a
    return tracer_network[mask]


def select_z(tracer_network, z):
    """Return subset of tracer network with given Z (atomic number)
    """
    mask = tracer_network['Z'] == z
    return tracer_network[mask]


# ===============================================================
#                      abu table
# ===============================================================
def select_abu(abu_table, tracer_network, z=None, a=None):
    """Return column(s) of abundance table with given Z and/or A
    """
    if z is None:
        if a is None:
            raise ValueError('Must specify at least one of Z, A')
        else:
            subset = select_abu_a(abu_table, tracer_network, a=a)
    else:
        if a is None:
            subset = select_abu_z(abu_table, tracer_network, z=z)
        else:
            isotope = get_isotope_str(z=z, a=a)
            subset = abu_table[isotope]

    return subset


def select_abu_a(abu_table, tracer_network, a):
    """Return subset of abundance table with given A (atomic mass number)
    """
    sub_net = select_a(tracer_network, a=a)
    return abu_table.iloc[:, sub_net.index]


def select_abu_z(abu_table, tracer_network, z):
    """Return subset of abundance table with given Z (atomic number)
    """
    sub_net = select_z(tracer_network, z=z)
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
