import numpy as np
import pandas as pd
import h5py

# nucleosynth
from . import paths
from .printing import printv

"""
Functions for loading/saving data
"""


def load_tracer_columns(tracer, model, columns=None, tracer_file=None,
                        verbose=True):
    """Load skynet tracer hdf5 file

    parameters
    ----------
    tracer : int
    model : str
    columns : [str]
        list of columns to extract
    tracer_file : h5py.File
        raw tracer file, as returned by load_tracer_file()
    verbose : bool
    """
    printv(f'Loading tracer columns', verbose=verbose)
    table = pd.DataFrame()

    if columns is None:
        columns = ['Time', 'Density', 'Temperature', 'Ye', 'HeatingRate', 'Entropy']

    tracer_file = load_tracer_file(tracer, model, tracer_file, verbose=verbose)

    for column in columns:
        table[column.lower()] = tracer_file[column]

    return table


def load_tracer_network(tracer, model, tracer_file=None, verbose=True):
    """Load isotope info (Z, A) for tracer

    parameters
    ----------
    tracer : int
    model : str
    tracer_file : h5py.File
    verbose : bool
    """
    printv(f'Loading tracer network', verbose=verbose)
    table = pd.DataFrame()
    tracer_file = load_tracer_file(tracer, model, tracer_file, verbose=verbose)

    for key in ['Z', 'A']:
        table[key] = np.array(tracer_file[key], dtype=int)

    return table


def load_abu(tracer, model, tracer_file=None, verbose=True):
    """Load chemical abundance table from tracer file

    parameters
    ----------
    tracer : int
    model : str
    tracer_file : h5py.File
    verbose : bool
    """
    printv(f'Loading tracer abundances', verbose=verbose)
    tracer_file = load_tracer_file(tracer, model, tracer_file, verbose=verbose)
    abu = pd.DataFrame(tracer_file['Y'])

    return abu


def load_tracer_file(tracer, model, tracer_file=None, verbose=True):
    """Load skynet tracer hdf5 file

    parameters
    ----------
    tracer : int
    model : str
    tracer_file : h5py.File
        if tracer_file provided, simply return
    verbose : bool
    """
    if tracer_file is None:
        filepath = paths.tracer_filepath(tracer, model=model)
        printv(f'Loading tracer file: {filepath}', verbose=verbose)
        tracer_file = h5py.File(filepath, 'r')

    return tracer_file
