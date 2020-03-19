import numpy as np
import pandas as pd

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


def get_network_unique(tracer_network):
    """Get unique Z and A in network

    Return : {'A': [int], 'Z': [int]}

    parameters
    ----------
    tracer_network : pd.DataFrame
    """
    network_unique = {}

    for group in ['A', 'Z']:
        network_unique[group] = np.unique(tracer_network[group])

    return network_unique


# ===============================================================
#                      summaries/subsets
# ===============================================================
def get_table_sums(table, tracer_network, group_by):
    """Calculate sums of abundance/mass-fraction over Z or A
        i.e., sum table columns grouped by either Z or A

    Returns : pd.DataFrame()
        where each column corresponds to the Z/A summed over

    parameters
    ----------
    table : pd.DataFrame
        Abundances or mass fractions
    tracer_network : pd.DataFrame
    group_by : one of ['A', 'Z']
        Which atomic number to group columns by
    """
    sums = pd.DataFrame()
    a = None
    z = None

    unique = np.unique(tracer_network[group_by])

    for num in unique:
        if group_by == 'A':
            a = num
        else:
            z = num

        subset = select_table(table, tracer_network=tracer_network, z=z, a=a)
        sums[num] = np.sum(subset, axis=1)

    return sums


# ===============================================================
#                      tables
# ===============================================================
def select_table(table, tracer_network, z=None, a=None):
    """Return column(s) of abundance table with given Z and/or A

    parameters
    ----------
    table : pd.DataFrame
        either abundance or mass_frac table
    tracer_network : pd.DataFrame
    z : int
    a : int
    """
    sub_net = select_network(tracer_network, z=z, a=a)
    return table.iloc[:, sub_net.index]


def get_mass_frac(abu_table, tracer_network):
    """Calculate mass fraction (X) table from abu table

    X = Y*A

    parameters
    ----------
    abu_table : pd.DataFrame
    tracer_network : pd.DataFrame
    """
    a = np.array(tracer_network['A'])
    return abu_table.multiply(a)


def get_ye(abu_table, tracer_network):
    """Calculate Ye from abu table

    Ye = sum(Z*X/A)
       = sum(Z*Y)

    parameters
    ----------
    abu_table : pd.DataFrame
    tracer_network : pd.DataFrame
    """
    z = np.array(tracer_network['Z'])
    zy = abu_table.multiply(z)
    return np.sum(zy, axis=1)


def get_zbar(abu_table, tracer_network, ye=None, abar=None):
    """Calculate Zbar from abu table

    Zbar = Ye*Abar

    parameters
    ----------
    abu_table : pd.DataFrame
    tracer_network : pd.DataFrame
    ye : 1d array
    abar : 1d array
    """
    if ye is None:
        ye = get_ye(abu_table, tracer_network)
    if abar is None:
        abar = get_abar(abu_table)

    return ye * abar


def get_abar(abu_table):
    """Calculate Abar from abu table

    Abar = 1/sumY

    parameters
    ----------
    abu_table : pd.DataFrame
    """
    sumy = get_sumy(abu_table)
    return 1 / sumy


def get_sumy(abu_table):
    """Calculate sumY from abu table

    sumY = sum(Y)
    Abar = 1/sumY

    parameters
    ----------
    abu_table : pd.DataFrame
    """
    return np.sum(abu_table, axis=1)


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


# ===============================================================
#                      convenience
# ===============================================================
def check_a_or_z(z, a):
    """Check that one (and only one) of A or Z has been specified
    """
    check_a_and_or_z(z=z, a=a, message='Must specify one of Z, A')

    if (z is not None) and (a is not None):
        raise ValueError('Can only specify one of Z, A')


def check_a_and_or_z(z, a, message='Must specify at least one of Z, A'):
    """Check that at least one of A or Z has been specified
    """
    if (z is None) and (a is None):
        raise ValueError(message)
