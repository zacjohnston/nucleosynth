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
from .config import tables_config

"""
Functions for loading/saving data
"""


# ===============================================================
#              Loading/extracting
# ===============================================================
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
def load_table(tracer_id, model, table_name, tracer_steps=(1, 2),
               columns=None, tracer_files=None, reload=False,
               save=True, verbose=True):
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
        raw tracer files to load and join, as returned by load_tracer_file()
        dict keys must correspond to tracer_steps
    reload : bool
        Force reload from raw skynet file
    save : bool
        save extracted table to cache
    verbose : bool
    """
    printv(f'Loading {table_name} table', verbose=verbose)
    table = None

    if not reload:
        try:
            table = load_table_cache(tracer_id, model, table_name, verbose=verbose)
        except FileNotFoundError:
            printv('cache not found', verbose)

    if table is None:
        printv(f'Reloading and joining {table_name} tables', verbose)

        table = extract_tracer_columns(tracer_id, tracer_steps=tracer_steps, model=model,
                                       columns=columns, tracer_files=tracer_files,
                                       verbose=verbose)

        if save:
            save_table_cache(table, tracer_id, model, 'columns', verbose=verbose)

    return table


def extract_table(tracer_id, tracer_steps, model, columns=None,
                           tracer_files=None, verbose=True):
    """Extract columns from skynet output file

    Returns : pd.DataFrame

    parameters
    ----------
    tracer_id : int
    tracer_steps : [int]
    model : str
    columns : [str]
    tracer_files : {h5py.File}
    verbose : bool
    """
    step_tables = []

    if columns is None:
        columns = tables_config.columns

    for step in tracer_steps:
        table = pd.DataFrame()
        printv(f'Extracting step {step}', verbose=verbose)

        tracer_file = load_tracer_file(tracer_id, step, model=model,
                                       tracer_file=tracer_files[step], verbose=verbose)
        for column in columns:
            table[column.lower()] = tracer_file[column]

        step_tables += [table]

    return pd.concat(step_tables, ignore_index=True)


def load_tracer_columns(tracer_id, model, tracer_steps=(1, 2),
                        columns=None, tracer_files=None, reload=False, save=True,
                        verbose=True):
    """Load columns from skynet tracer output, and join tables

    Returns : pd.DataFrame

    parameters
    ----------
    tracer_id : int
    model : str
    tracer_steps : [int]
        Load multiple skynet files for joining
    columns : [str]
        list of columns to extract
    tracer_files : {h5py.File}
        raw tracer files to load and join, as returned by load_tracer_file()
        dict keys must correspond to tracer_steps
    reload : bool
        Force reload from raw skynet file
    save : bool
        save extracted table to cache
    verbose : bool
    """
    printv(f'Loading tracer columns', verbose=verbose)
    table = None

    if not reload:
        try:
            table = load_table_cache(tracer_id, model, 'columns', verbose=verbose)
        except FileNotFoundError:
            printv('cache not found', verbose)

    if table is None:
        printv('Reloading and joining column tables', verbose)

        table = extract_tracer_columns(tracer_id, tracer_steps=tracer_steps, model=model,
                                       columns=columns, tracer_files=tracer_files, verbose=verbose)

        if save:
            save_table_cache(table, tracer_id, model, 'columns', verbose=verbose)

    return table


def extract_tracer_columns(tracer_id, tracer_steps, model, columns=None,
                           tracer_files=None, verbose=True):
    """Extract columns from skynet output file

    Returns : pd.DataFrame

    parameters
    ----------
    tracer_id : int
    tracer_steps : [int]
    model : str
    columns : [str]
    tracer_files : {h5py.File}
    verbose : bool
    """
    step_tables = []

    if columns is None:
        columns = tables_config.columns

    for step in tracer_steps:
        table = pd.DataFrame()
        printv(f'Extracting step {step}', verbose=verbose)

        tracer_file = load_tracer_file(tracer_id, step, model=model,
                                       tracer_file=tracer_files[step], verbose=verbose)
        for column in columns:
            table[column.lower()] = tracer_file[column]

        step_tables += [table]

    return pd.concat(step_tables, ignore_index=True)


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
#              Abundance
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