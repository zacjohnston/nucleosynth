import numpy as np
import pandas as pd
import h5py

# nucleosynth
from . import paths
from . import network
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


def load_tracer_abu(tracer, model, tracer_file=None, tracer_network=None,
                    verbose=True):
    """Load chemical abundance table from tracer file

    parameters
    ----------
    tracer : int
    model : str
    tracer_file : h5py.File
    tracer_network : pd.DataFrame
    verbose : bool
    """
    printv(f'Loading tracer abundances', verbose=verbose)

    tracer_file = load_tracer_file(tracer, model, tracer_file, verbose=verbose)
    tracer_network = load_tracer_network(tracer, model, tracer_file, verbose=verbose)

    tracer_abu = pd.DataFrame(tracer_file['Y'])
    tracer_abu.columns = list(tracer_network['isotope'])

    return tracer_abu


def load_tracer_network(tracer, model, tracer_file=None, tracer_network=None,
                        verbose=True):
    """Load isotope info (Z, A) used in tracer

    parameters
    ----------
    tracer : int
    model : str
    tracer_file : h5py.File
    tracer_network : pd.DataFrame
    verbose : bool
    """
    printv(f'Loading tracer network', verbose=verbose)

    tracer_file = load_tracer_file(tracer, model, tracer_file, verbose=verbose)
    
    if tracer_network is None:
        tracer_network = pd.DataFrame()
        iso_list = []

        for key in ['Z', 'A']:
            tracer_network[key] = np.array(tracer_file[key], dtype=int)

        for i in range(len(tracer_network)):
            row = tracer_network.loc[i]
            iso_str = network.get_isotope_str(z=row['Z'], a=row['A'])
            iso_list += [iso_str]

        tracer_network['isotope'] = iso_list
        tracer_network = tracer_network[['isotope', 'Z', 'A']]

    return tracer_network


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
