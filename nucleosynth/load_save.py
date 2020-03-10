import numpy as np
import pandas as pd
import h5py
import os
import subprocess
import sys

# nucleosynth
from . import paths
from . import network
from .printing import printv

"""
Functions for loading/saving data
"""


# ===============================================================
#              Loading/extracting
# ===============================================================
def load_tracer_abu(tracer_id, tracer_step, model, tracer_file=None,
                    tracer_network=None, verbose=True):
    """Load chemical abundance table from tracer file

    parameters
    ----------
    tracer_id : int
    tracer_step : 1 or 2
    model : str
    tracer_file : h5py.File
    tracer_network : pd.DataFrame
    verbose : bool
    """
    printv(f'Loading tracer abundances', verbose=verbose)

    tracer_file = load_tracer_file(tracer_id, tracer_step, model=model,
                                   tracer_file=tracer_file, verbose=verbose)

    tracer_network = load_tracer_network(tracer_id, tracer_step, model=model,
                                         tracer_file=tracer_file,
                                         tracer_network=tracer_network, verbose=verbose)

    tracer_abu = pd.DataFrame(tracer_file['Y'])
    tracer_abu.columns = list(tracer_network['isotope'])

    return tracer_abu


def load_tracer_network(tracer_id, tracer_step, model, tracer_file=None,
                        tracer_network=None, verbose=True):
    """Load isotope info (Z, A) used in tracer

    parameters
    ----------
    tracer_id : int
    tracer_step : 1 or 2
    model : str
    tracer_file : h5py.File
    tracer_network : pd.DataFrame
    verbose : bool
    """
    tracer_file = load_tracer_file(tracer_id, tracer_step, model=model,
                                   tracer_file=tracer_file, verbose=verbose)

    if tracer_network is None:
        printv(f'Loading tracer network', verbose=verbose)
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


def load_tracer_file(tracer_id, tracer_step, model, tracer_file=None, verbose=True):
    """Load skynet tracer hdf5 file

    parameters
    ----------
    tracer_id : int
    tracer_step : 1 or 2
    model : str
    tracer_file : h5py.File
        if tracer_file provided, simply return
    verbose : bool
    """
    if tracer_file is None:
        filepath = paths.tracer_filepath(tracer_id, tracer_step, model=model)
        printv(f'Loading tracer file: {filepath}', verbose=verbose)
        tracer_file = h5py.File(filepath, 'r')

    return tracer_file


# ===============================================================
#              Columns
# ===============================================================
def load_tracer_columns(tracer_id, tracer_step, model, columns=None,
                        tracer_file=None, verbose=True):
    """Load columns from skynet tracer output

    parameters
    ----------
    tracer_id : int
    tracer_step : 1 or 2
    model : str
    columns : [str]
        list of columns to extract
    tracer_file : h5py.File
        raw tracer file, as returned by load_tracer_file()
    verbose : bool
    """
    printv(f'Loading tracer columns', verbose=verbose)
    table = extract_tracer_columns(tracer_id, tracer_step, model=model, columns=columns,
                                   tracer_file=tracer_file, verbose=verbose)

    return table


def extract_tracer_columns(tracer_id, tracer_step, model, columns=None,
                           tracer_file=None, verbose=True):
    """Extract columns from skynet tracer output
    """
    table = pd.DataFrame()

    if columns is None:
        columns = ['Time', 'Density', 'Temperature', 'Ye', 'HeatingRate', 'Entropy']

    tracer_file = load_tracer_file(tracer_id, tracer_step, model=model,
                                   tracer_file=tracer_file, verbose=verbose)

    for column in columns:
        table[column.lower()] = tracer_file[column]

    return table


def save_columns_cache(table, tracer_id, model, verbose=True):
    """Save columns table to file

    parameters
    ----------
    table : pd.DataFrame
    tracer_id : int
    model : str
    verbose : bool
    """
    check_model_cache_path(model, verbose=verbose)
    filepath = paths.columns_cache_filepath(tracer_id, model)
    printv(f'Saving columns: {filepath}', verbose)
    table.to_pickle(filepath)


def load_columns_cache(tracer_id, model, verbose=True):
    """Load columns table from pre-cached file

    parameters
    ----------
    tracer_id : int
    model : str
    verbose : bool
    """
    filepath = paths.columns_cache_filepath(tracer_id, model)
    printv(f'Loading columns cache: {filepath}', verbose)
    return pd.read_pickle(filepath)


# ===============================================================
#              Misc.
# ===============================================================
def check_model_cache_path(model, verbose=True):
    """Check that the model cache directory exists
    """
    path = paths.model_cache_path(model)
    try_mkdir(path, skip=True, verbose=verbose)


def try_mkdir(path, skip=False, verbose=True):
    """Try to create directory

    parameters
    ----------
    path: str
        Full path to directory to create
    skip : bool
        do nothing if directory already exists
        if skip=false, will ask to overwrite an existing directory
    verbose : bool
    """
    printv(f'Creating directory  {path}', verbose)
    if os.path.exists(path):
        if skip:
            printv('Directory already exists', verbose)
        else:
            print('Directory exists')
            cont = input('Overwrite (DESTROY)? (y/[n]): ')

            if cont == 'y' or cont == 'Y':
                subprocess.run(['rm', '-r', path])
                subprocess.run(['mkdir', path])
            else:
                sys.exit()
    else:
        subprocess.run(['mkdir', '-p', path], check=True)