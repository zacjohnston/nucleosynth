import numpy as np
import pandas as pd
import h5py

# nucleosynth
from nucleosynth import paths, network
from nucleosynth.tracers import extract
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
               abu_table=None, reload=False, save=True, verbose=True):
    """Generalised wrapper function for loading tracer tables

    Main steps:
        1. Tries to load from cache
        2. If no cache, re-extract from file or existing table
        3. Save new table to cache (if save=True)

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
    abu_table : pd.DataFrame
    reload : bool
        Force reload from raw skynet file
    save : bool
        save extracted table to cache
    verbose : bool
    """
    printv(f'Loading {table_name} table', verbose=verbose)
    table = None

    if table_name not in ['columns', 'network', 'abu', 'mass_frac']:
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
                              tracer_network=tracer_network, abu_table=abu_table,
                              tracer_files=tracer_files, verbose=verbose)
        if save:
            save_table_cache(table, tracer_id, model, table_name, verbose=verbose)

    return table


def extract_table(tracer_id, tracer_steps, model, table_name, columns=None,
                  tracer_files=None, tracer_network=None, abu_table=None,
                  verbose=True):
    """Wrapper for various table extract functions

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
    abu_table : pd.DataFrame
    verbose : bool
    """
    step_tables = []

    if columns is None:
        columns = tables_config.columns

    tracer_files = load_files(tracer_id, model=model, tracer_steps=tracer_steps,
                              tracer_files=tracer_files, verbose=verbose)

    if tracer_network is None:
        tracer_network = extract.extract_network(tracer_files[tracer_steps[0]])

    if table_name == 'network':
        return tracer_network

    for step in tracer_steps:
        tracer_file = tracer_files[step]

        if table_name == 'columns':
            table = extract.extract_columns(tracer_file, columns=columns)

        elif table_name == 'abu':
            table = extract.extract_abu(tracer_file, tracer_network=tracer_network)

        elif table_name == 'mass_frac':
            if abu_table is None:
                abu_table = load_table(tracer_id, model=model, tracer_steps=tracer_steps,
                                       table_name='abu', tracer_files=tracer_files,
                                       tracer_network=tracer_network, verbose=verbose)

            table = network.get_mass_frac(abu_table, tracer_network=tracer_network)

        else:
            raise ValueError('table_name must be one of: columns, abu, mass_frac ')

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
    printv(f'Saving table to cache: {filepath}', verbose)
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
    printv(f'Loading table from cache: {filepath}', verbose)
    return pd.read_pickle(filepath)


def check_model_cache_path(model, verbose=True):
    """Check that the model cache directory exists
    """
    path = paths.model_cache_path(model)
    paths.try_mkdir(path, skip=True, verbose=verbose)
