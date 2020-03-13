import numpy as np
import pandas as pd
import h5py
import os
import subprocess
import sys

# nucleosynth
from nucleosynth import paths
from nucleosynth import network
from nucleosynth.printing import printv
from nucleosynth.config import tables_config

"""
Functions for loading/saving tracer data
"""


# ===============================================================
#              Loading/extracting
# ===============================================================
def load_files(tracer_id, model, tracer_steps,
               tracer_files=None, verbose=True):
    """Load multiple skynet tracer files

    parameters
    ----------
    tracer_id : int
    tracer_steps : [int]
    model : str
    tracer_files : h5py.File
    verbose : bool
    """
    if tracer_files is None:
        tracer_files = {}

        for step in tracer_steps:
            tracer_files[step] = load_file(tracer_id, tracer_step=step,
                                           model=model, verbose=verbose)

    return tracer_files


def load_file(tracer_id, tracer_step, model, tracer_file=None, verbose=True):
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


def load_table(tracer_id, model, table_name, tracer_steps,
               columns=None, tracer_files=None, tracer_network=None,
               reload=False, save=True, verbose=True):
    """Generalised function for loading tracer tables

    Returns : pd.DataFrame

    parameters
    ----------
    tracer_id : int
    model : str
    table_name : one of ('columns', 'abu', 'mass_frac', 'network')
    tracer_steps : [int]
        Load multiple skynet files for joining
    columns : [str]
        list of columns to extract
    tracer_files : {h5py.File}
        raw tracer files to load and join, as returned by load_file()
        dict keys must correspond to tracer_steps
    tracer_network : pd.DataFrame
    reload : bool
        Force reload from raw skynet file
    save : bool
        save extracted table to cache
    verbose : bool
    """
    printv(f'Loading {table_name} table', verbose=verbose)
    table = None

    if table_name not in ['columns', 'network', 'abu']:
        raise ValueError('table_name must be one of: columns, abu, mass_frac ')

    if not reload:
        try:
            table = load_table_cache(tracer_id, model, table_name, verbose=verbose)
        except FileNotFoundError:
            printv('cache not found', verbose)

    if table is None:
        printv(f'Reloading and joining {table_name} tables', verbose)

        table = extract_table(tracer_id, tracer_steps=tracer_steps, model=model,
                              table_name=table_name, columns=columns,
                              tracer_network=tracer_network,
                              tracer_files=tracer_files, verbose=verbose)
        if save:
            save_table_cache(table, tracer_id, model, table_name, verbose=verbose)

    return table


def extract_table(tracer_id, tracer_steps, model, table_name, columns=None,
                  tracer_files=None, tracer_network=None, verbose=True):
    """Extract and join table from multiple skynet output files

    Returns : pd.DataFrame

    parameters
    ----------
    tracer_id : int
    tracer_steps : [int]
    model : str
    table_name : str
    columns : [str]
    tracer_files : {h5py.File}
    tracer_network : pd.DataFrame
    verbose : bool
    """
    step_tables = []

    if columns is None:
        columns = tables_config.columns

    tracer_files = load_files(tracer_id, model=model, tracer_steps=tracer_steps,
                              tracer_files=tracer_files, verbose=verbose)

    if tracer_network is None:
        tracer_network = extract_network(tracer_files[tracer_steps[0]])

    if table_name == 'network':
        return tracer_network

    for step in tracer_steps:
        tracer_file = tracer_files[step]

        if table_name == 'columns':
            table = extract_columns(tracer_file, columns=columns)
        elif table_name == 'abu':
            table = extract_abu(tracer_file, tracer_network=tracer_network)
        else:
            raise ValueError('table_name must be one of: columns, abu, mass_frac ')

        step_tables += [table]

    return pd.concat(step_tables, ignore_index=True)


# ===============================================================
#              Columns
# ===============================================================
def extract_columns(tracer_file, columns=None):
    """Extract table of columns from a skynet output file

    Returns : pd.DataFrame

    parameters
    ----------
    tracer_file : h5py.File
    columns : [str]
    """
    table = pd.DataFrame()

    if columns is None:
        columns = tables_config.columns

    for column in columns:
        table[column.lower()] = tracer_file[column]

    return table


# ===============================================================
#              Network
# ===============================================================
def load_network(tracer_id, tracer_step, model, tracer_file=None,
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
    printv(f'Loading tracer network', verbose=verbose)
    tracer_file = load_file(tracer_id, tracer_step, model=model,
                            tracer_file=tracer_file, verbose=verbose)

    if tracer_network is None:
        tracer_network = extract_network(tracer_file)

    return tracer_network


def extract_network(tracer_file):
    """Extract tracer network of isotopes from skynet output file

    parameters
    ----------
    tracer_file : h5py.File
    """
    tracer_network = pd.DataFrame()
    iso_list = []

    for key in ['Z', 'A']:
        tracer_network[key] = np.array(tracer_file[key], dtype=int)

    for i in range(len(tracer_network)):
        row = tracer_network.loc[i]
        iso_str = network.get_isotope_str(z=row['Z'], a=row['A'])
        iso_list += [iso_str]

    tracer_network['isotope'] = iso_list
    return tracer_network[['isotope', 'Z', 'A']]


# ===============================================================
#              Abundance
# ===============================================================
def extract_abu(tracer_file, tracer_network):
    """Extract table of chemical abundances from skynet tracer file

    parameters
    ----------
    tracer_file : h5py.File
    tracer_network : pd.DataFrame
    """
    tracer_abu = pd.DataFrame(tracer_file['Y'])
    tracer_abu.columns = list(tracer_network['isotope'])
    return tracer_abu


# ===============================================================
#              Cache
# ===============================================================
def save_table_cache(table, tracer_id, model, table_name, verbose=True):
    """Save columns table to file

    parameters
    ----------
    table : pd.DataFrame
    tracer_id : int
    model : str
    table_name : one of ('columns', 'abu', 'mass_frac', 'network')
    verbose : bool
    """
    check_model_cache_path(model, verbose=verbose)
    filepath = paths.cache_filepath(tracer_id, model, table_name=table_name)
    printv(f'Saving columns table: {filepath}', verbose)
    table.to_pickle(filepath)


def load_table_cache(tracer_id, model, table_name, verbose=True):
    """Load columns table from pre-cached file

    parameters
    ----------
    tracer_id : int
    model : str
    table_name : one of ('columns', 'abu', 'mass_frac', 'network')
    verbose : bool
    """
    filepath = paths.cache_filepath(tracer_id, model, table_name=table_name)
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