import numpy as np
import pandas as pd
import h5py

# nucleosynth
from . import paths
from .printing import printv

"""
Functions for loading/saving data
"""


def load_tracer_columns(tracer, model, verbose=True,
                        columns=('Time', 'Density', 'Temperature', 'Ye', 'HeatingRate', 'Entropy')):
    """Load skynet tracer hdf5 file

    parameters
    ----------
    tracer : int
    model : str
    columns : [str]
        columns to extract
    verbose : bool
    """
    printv(f'Loading tracer columns', verbose=verbose)
    table = pd.DataFrame()

    f = load_tracer_hdf5(tracer, model)

    for column in columns:
        table[column.lower()] = f[column]

    return table


def load_tracer_network(tracer, model, verbose=True):
    """Load isotope info (Z, A) for tracer

    parameters
    ----------
    tracer : int
    model : str
    verbose : bool
    """
    printv(f'Loading tracer network', verbose=verbose)
    table = pd.DataFrame()
    f = load_tracer_hdf5(tracer, model)

    for key in ['Z', 'A']:
        table[key] = np.array(f[key], dtype=int)

    return table


def load_abu(tracer, model, verbose=True):
    """Load chemical abundance table from tracer file

    parameters
    ----------
    tracer : int
    model : str
    verbose : bool
    """
    printv(f'Loading tracer abundances', verbose=verbose)
    f = load_tracer_hdf5(tracer, model)
    abu = pd.DataFrame(f['Y'])

    return abu


def load_tracer_hdf5(tracer, model, verbose=True):
    """Load skynet tracer hdf5 file

    parameters
    ----------
    tracer : int
    model : str
    verbose : bool
    """
    filepath = paths.tracer_filepath(tracer, model=model)
    printv(f'Loading tracer hdf5: {filepath}', verbose=verbose)

    f = h5py.File(filepath, 'r')
    return f
