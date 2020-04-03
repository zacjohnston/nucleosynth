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
def select_isotopes(isotope_table, a=None, z=None):
    """Return subset of isotope table that matches given A and/or Z

    parameters
    ----------
    isotope_table : pd.DataFrame
        table containing A and Z columns (e.g., tracer_network)
    z : int
    a : int
    """
    if (z is None) and (a is None):
        raise ValueError('Must specify at least one of Z, A')

    z_mask = isotope_table['Z'] == z
    a_mask = isotope_table['A'] == a

    if None in [z, a]:
        mask = np.logical_or(z_mask, a_mask)
    else:
        mask = np.logical_and(z_mask, a_mask)

    return isotope_table[mask]


def get_network_unique(tracer_network):
    """Get unique Z and A in network

    Returns : {'A': [int], 'Z': [int]}

    parameters
    ----------
    tracer_network : pd.DataFrame
    """
    network_unique = {}

    for group in ['A', 'Z']:
        network_unique[group] = np.unique(tracer_network[group])

    return network_unique


# ===============================================================
#                      sums
# ===============================================================
def get_all_sums(composition, tracer_network):
    """Get all X, Y sums over A, Z

    Returns : {'A': {'X': pd.DataFrame, 'Y': pd.DataFrame},
               'Z': {'X': pd.DataFrame, 'Y': pd.DataFrame}}

    parameters
    ----------
    composition : {'X': pd.DataFrame, 'Y': pd.DataFrame}
    tracer_network : pd.DataFrame
    """
    sums = {'A': {}, 'Z': {}}

    for group in sums:
        for comp_key, comp_table in composition.items():
            sums[group][comp_key] = get_sums(comp_table,
                                             tracer_network=tracer_network,
                                             group=group)
    return sums


def get_sums(composition_table, tracer_network, group):
    """Calculate sums of X and Y for fixed Z or A
        i.e., sum table columns grouped by either Z or A

    Returns : pd.DataFrame()
        where each column corresponds to the Z/A summed over

    parameters
    ----------
    composition_table : pd.DataFrame
        X or Y table
    tracer_network : pd.DataFrame
    group : one of ['A', 'Z']
        Which atomic number to group columns by
    """
    sums = pd.DataFrame()
    a = None
    z = None

    unique = np.unique(tracer_network[group])

    for val in unique:
        if group == 'A':
            a = val
        else:
            z = val

        subset = select_composition(composition_table, tracer_network=tracer_network,
                                    z=z, a=a)
        sums[val] = np.sum(subset, axis=1)

    return sums


# ===============================================================
#                      yields
# ===============================================================
def get_yields(tracers, tracer_network):
    """Sum over all tracers to obtain final composition yields

    Returns : pd.DataFrame

    parameters
    ----------
    tracers : {tracer_id: Tracer}
    tracer_network : pd.DataFrame
    """
    yields = pd.DataFrame(tracer_network)
    n_tracers = len(tracers)

    for group in ['X', 'Y']:
        yields[group] = 0.0

        for tracer_id, tracer in tracers.items():
            last_row = tracer.composition[group].iloc[-1]
            yields[group] += np.array(last_row) / n_tracers

    return yields


def get_all_yield_sums(yields):
    """Sum over yields grouped by both A and Z

    Returns : {'A': pd.DataFrame, 'Z': pd.DataFrame}

    parameters
    ----------
    yields : pd.DataFrame
    """
    yield_sums = {'A': None, 'Z': None}

    for group in yield_sums:
        yield_sums[group] = get_yield_sums(yields, group=group)

    return yield_sums


def get_yield_sums(yields, group):
    """Sum over yields grouped by A or Z

    Returns : pd.DataFrame

    parameters
    ----------
    yields : pd.DataFrame
    group : one of ['A', 'Z']
    """
    yield_sums = pd.DataFrame()
    group_unique = np.unique(yields[group])

    sums = {}
    for abu in ['X', 'Y']:
        sums[abu] = np.full(len(group_unique), np.nan)

    a = None
    z = None

    # TODO: check to properly weight by A, Z?
    for i, val in enumerate(group_unique):
        if group == 'A':
            a = val
        else:
            z = val

        subset = select_isotopes(yields, a=a, z=z)

        for abu in ['X', 'Y']:
            sums[abu][i] = np.sum(subset[abu])

    yield_sums[group] = group_unique

    for abu in ['X', 'Y']:
        yield_sums[abu] = sums[abu]

    return yield_sums


# ===============================================================
#                      tables
# ===============================================================
def select_composition(composition_table, tracer_network, z=None, a=None):
    """Return subset of X or Y table with given Z and/or A

    Returns : pd.DataFrame

    parameters
    ----------
    composition_table : pd.DataFrame
        X or Y table
    tracer_network : pd.DataFrame
    z : int
    a : int
    """
    sub_net = select_isotopes(tracer_network, z=z, a=a)
    return composition_table.iloc[:, sub_net.index]


def get_x(y_table, tracer_network):
    """Calculate X table from Y table

    X = Y*A

    Returns : pd.DataFrame

    parameters
    ----------
    y_table : pd.DataFrame
    tracer_network : pd.DataFrame
    """
    a = np.array(tracer_network['A'])
    return y_table.multiply(a)


def get_ye(y_table, tracer_network):
    """Calculate Ye from Y table

    Ye = sum(Z*X/A)
       = sum(Z*Y)

    Returns : pd.Series

    parameters
    ----------
    y_table : pd.DataFrame
    tracer_network : pd.DataFrame
    """
    z = np.array(tracer_network['Z'])
    zy = y_table.multiply(z)
    return np.sum(zy, axis=1)


def get_zbar(y_table, tracer_network, ye=None, abar=None):
    """Calculate Zbar from Y table

    Zbar = Ye*Abar

    Returns : pd.Series

    parameters
    ----------
    y_table : pd.DataFrame
    tracer_network : pd.DataFrame
    ye : 1d array
    abar : 1d array
    """
    if ye is None:
        ye = get_ye(y_table, tracer_network)
    if abar is None:
        abar = get_abar(y_table)

    return ye * abar


def get_abar(y_table):
    """Calculate Abar from Y table

    Abar = 1/sumY

    Returns : pd.Series

    parameters
    ----------
    y_table : pd.DataFrame
    """
    sumy = get_sumy(y_table)
    return 1 / sumy


def get_sumy(y_table):
    """Calculate sumY from Y table

    sumY = sum(Y)
    Abar = 1/sumY

    Returns : pd.Series

    parameters
    ----------
    y_table : pd.DataFrame
    """
    return np.sum(y_table, axis=1)


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


def sums_table_name(composition_type, group):
    """Return formatted table name for composition sums

    parameters
    ----------
    composition_type : 'X' or 'Y'
    group : 'A' or 'Z'
    """
    return f'sums_{group}_{composition_type}'


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
