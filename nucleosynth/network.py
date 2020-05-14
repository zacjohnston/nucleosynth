import numpy as np
import pandas as pd

# nucleosynth
from .config import elements

"""
Functions for managing nuclear network data

common arguments/variables
----------------------------
abu_var : 'X' or 'Y'
    Mass fraction (X) or number fraction (Y)
composition_table : pd.DataFrame
    X or Y table
iso_group : 'A' or 'Z'
    Nuclides grouped by A (isobars) or Z (isotopes)
isotope_table : pd.DataFrame
    Any table containing both A and Z columns (e.g., tracer_network)
tracer_network : pd.DataFrame
    Table of isotopes used in a model (columns: isotope, Z, A)
    
"""


# ===============================================================
#                      network table
# ===============================================================
def select_isotopes(isotope_table, a=None, z=None):
    """Return subset of table with given A and/or Z

    parameters
    ----------
    isotope_table : pd.DataFrame
        any table containing both A and Z columns (e.g., tracer_network)
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
    """Get unique A and Z in network

    Returns : {iso_group: [int]}

    parameters
    ----------
    tracer_network : pd.DataFrame
    """
    network_unique = {}

    for iso_group in ['A', 'Z']:
        network_unique[iso_group] = np.unique(tracer_network[iso_group])

    return network_unique


# ===============================================================
#                      composition
# ===============================================================
def get_most_abundant(composition_table, tracer_network, n=10):
    """Return subset of network table of most abundant isotopes

    Returns : pd.DataFrame
        subset of tracer_network, with a 'max_value' column

    parameters
    ----------
    composition_table : pd.DataFrame
        X or Y table
    tracer_network : pd.DataFrame
    n : int
        find 'n' most abundant isotopes
    """
    isotopes = tracer_network.copy()

    max_values = composition_table.max()
    isotopes['max_value'] = max_values.values

    return isotopes.nlargest(n, 'max_value')


# ===============================================================
#                      sums
# ===============================================================
def get_all_sums(composition, tracer_network):
    """Get all X, Y sums over A, Z

    Returns : {iso_group: {abu_var: pd.DataFrame}}

    parameters
    ----------
    composition : {abu_var: pd.DataFrame}
    tracer_network : pd.DataFrame
    """
    sums = {'A': {}, 'Z': {}}

    for iso_group in sums:
        for comp_key, comp_table in composition.items():
            sums[iso_group][comp_key] = get_sums(comp_table,
                                                 tracer_network=tracer_network,
                                                 iso_group=iso_group)
    return sums


def get_sums(composition_table, tracer_network, iso_group):
    """Calculate sums of X and Y for fixed Z or A
        i.e., sum table columns grouped by either Z or A

    Returns : pd.DataFrame()
        where each column corresponds to the Z/A summed over

    parameters
    ----------
    composition_table : pd.DataFrame
        X or Y table
    tracer_network : pd.DataFrame
    iso_group : 'A' or 'Z'
        Which atomic number to group columns by
    """
    sums = pd.DataFrame()
    a = None
    z = None

    unique = np.unique(tracer_network[iso_group])

    for val in unique:
        if iso_group == 'A':
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
def get_yields(tracers, tracer_network, abu_vars=('X', 'Y')):
    """Sum over all tracers to obtain final composition yields

    Returns : pd.DataFrame

    parameters
    ----------
    tracers : {tracer_id: Tracer}
    tracer_network : pd.DataFrame
    abu_vars : [str]
    """
    yields = pd.DataFrame(tracer_network)
    n_tracers = len(tracers)

    for abu_var in abu_vars:
        yields[abu_var] = 0.0

        for tracer_id, tracer in tracers.items():
            last_row = tracer.composition[abu_var].iloc[-1]
            yields[abu_var] += np.array(last_row) / n_tracers

    return yields


def get_all_yield_sums(yields):
    """Sum over yields grouped by both A and Z

    Returns : {iso_group: pd.DataFrame}

    parameters
    ----------
    yields : pd.DataFrame
    """
    yield_sums = {'A': None, 'Z': None}

    for iso_group in yield_sums:
        yield_sums[iso_group] = get_yield_sums(yields, iso_group=iso_group)

    return yield_sums


def get_yield_sums(yields, iso_group, abu_vars=('X', 'Y')):
    """Sum over yields grouped by A or Z

    Returns : pd.DataFrame

    parameters
    ----------
    yields : pd.DataFrame
    iso_group : 'A' or 'Z'
    abu_vars : [str]
        which abundance variables to extract (X and/or Y)
    """
    yield_sums = pd.DataFrame()
    group_unique = np.unique(yields[iso_group])

    sums = {}
    for abu_var in abu_vars:
        sums[abu_var] = np.full(len(group_unique), np.nan)

    a = None
    z = None

    # TODO: check to properly weight by A, Z?
    for i, val in enumerate(group_unique):
        if iso_group == 'A':
            a = val
        else:
            z = val

        subset = select_isotopes(yields, a=a, z=z)

        for abu_var in abu_vars:
            sums[abu_var][i] = np.sum(subset[abu_var])

    yield_sums[iso_group] = group_unique

    for abu_var in abu_vars:
        yield_sums[abu_var] = sums[abu_var]

    return yield_sums


# ===============================================================
#                      tables
# ===============================================================
def select_composition(composition_table, tracer_network, z=None, a=None):
    """Return subset of X or Y table with given A and/or Z

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


def sums_table_name(abu_var, iso_group):
    """Return formatted table name for composition sums

    parameters
    ----------
    abu_var : 'X' or 'Y'
    iso_group : 'A' or 'Z'
    """
    return f'sums_{iso_group}_{abu_var}'


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
