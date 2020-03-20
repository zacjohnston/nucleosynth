import numpy as np
import pandas as pd
import h5py

# nucleosynth
from nucleosynth import paths, network, tools
from nucleosynth.tracers import extract
from nucleosynth.printing import printv
from nucleosynth.config import tables_config

"""
Functions for loading/saving tracer data
"""


# ===============================================================
#              Loading/extracting tables
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
               y_table=None, reload=False, save=True, verbose=True):
    """Wrapper function for loading various tracer tables

    Main steps:
        1. Try to load from cache
        2. If no cache, re-extract from file
        3. Save new table to cache (if save=True)

    Returns : pd.DataFrame

    parameters
    ----------
    tracer_id : int
    model : str
    table_name : one of ('columns', 'X', 'Y', 'network')
    tracer_steps : [int]
        Load multiple skynet files for joining
    columns : [str]
        list of columns to extract
    tracer_files : {h5py.File}
        raw tracer files to load and join, as returned by load_file()
        dict keys must correspond to tracer_steps
    tracer_network : pd.DataFrame
    y_table : pd.DataFrame
    reload : bool
        Force reload from raw skynet file
    save : bool
        save extracted table to cache
    verbose : bool
    """
    printv(f'Loading {table_name} table', verbose=verbose)
    table = None

    if table_name not in ['columns', 'network', 'X', 'Y']:
        raise ValueError('table_name must be one of: columns, X, Y')

    if not reload:
        try:
            table = load_table_cache(tracer_id, model, table_name, verbose=verbose)
        except FileNotFoundError:
            printv('cache not found', verbose)

    if table is None:
        printv(f'Reloading and joining {table_name} tables', verbose)

        table = extract_table(tracer_id, tracer_steps=tracer_steps, model=model,
                              table_name=table_name, columns=columns,
                              tracer_network=tracer_network, y_table=y_table,
                              tracer_files=tracer_files, verbose=verbose)
        if save:
            save_table_cache(table, tracer_id, model, table_name, verbose=verbose)

    return table


def extract_table(tracer_id, tracer_steps, model, table_name, columns=None,
                  tracer_files=None, tracer_network=None, y_table=None,
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
    y_table : pd.DataFrame
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

    if table_name == 'X':
        if y_table is None:
            y_table = extract_table(tracer_id, tracer_steps=tracer_steps,
                                    model=model, table_name='Y',
                                    tracer_files=tracer_files,
                                    tracer_network=tracer_network, verbose=verbose)

        return network.get_x(y_table, tracer_network=tracer_network)

    for step in tracer_steps:
        tracer_file = tracer_files[step]

        if table_name == 'columns':
            table = extract.extract_columns(tracer_file, columns=columns)

        elif table_name == 'Y':
            table = extract.extract_y(tracer_file, tracer_network=tracer_network)

        else:
            raise ValueError('table_name must be one of (network, columns, X, Y)')

        step_tables += [table]

    return pd.concat(step_tables, ignore_index=True)


# ===============================================================
#              Composition
# ===============================================================
def load_composition(tracer_id, tracer_steps, model,
                     tracer_files=None, tracer_network=None,
                     reload=False, save=True, verbose=True):
    """Wrapper function to load both composition tables (X, Y)

    Returns : {'X': pd.DataFrame, 'Y': pd.DataFrame}

    parameters
    ----------
    tracer_id : int
    tracer_steps : [int]
    model : str
    tracer_files : {h5py.File}
    tracer_network : pd.DataFrame
    reload : bool
    save : bool
    verbose : bool
    """
    composition = {}

    for key in ['X', 'Y']:
        composition[key] = load_table(tracer_id,
                                      tracer_steps=tracer_steps,
                                      model=model,
                                      tracer_files=tracer_files,
                                      table_name=key,
                                      tracer_network=tracer_network,
                                      save=save, reload=reload,
                                      verbose=verbose)
    return composition


def load_composition_sums(tracer_id, tracer_steps, model,
                          tracer_files=None, tracer_network=None,
                          composition=None,
                          reload=False, save=True, verbose=True):
    """Wrapper function to load all composition sum tables

    Returns : {'A': {'X': pd.DataFrame, 'Y': pd.DataFrame},
               'Z': {'X': pd.DataFrame, 'Y': pd.DataFrame}}

    parameters
    ----------
    tracer_id : int
    tracer_steps : [int]
    model : str
    tracer_files : {h5py.File}
    tracer_network : pd.DataFrame
    reload : bool
    save : bool
    verbose : bool
    """
    printv(f'Loading composition sum tables', verbose=verbose)
    sums = None

    if not reload:
        try:
            sums = load_composition_sums_cache(tracer_id, model=model, verbose=verbose)
        except FileNotFoundError:
            printv('cache not found', verbose)

    if sums is None:
        printv(f'Calculating sums', verbose)
        tracer_files = load_files(tracer_id, tracer_steps=tracer_steps, model=model,
                                  tracer_files=tracer_files, verbose=verbose)

        if composition is None:
            composition = load_composition(tracer_id, tracer_steps=tracer_steps,
                                           model=model, tracer_files=tracer_files,
                                           tracer_network=tracer_network,
                                           reload=reload, save=save, verbose=verbose)

        if tracer_network is None:
            tracer_network = load_table(tracer_id, tracer_steps=tracer_steps,
                                        model=model, table_name='network',
                                        tracer_files=tracer_files, reload=reload,
                                        save=save, verbose=verbose)

        sums = network.get_all_composition_sums(composition, tracer_network=tracer_network)

        if save:
            save_composition_sums_cache(tracer_id, model=model,
                                        composition_sums=sums, verbose=verbose)

    return sums


def save_composition_sums_cache(tracer_id, model, composition_sums, verbose=True):
    """Save composition sum tables to cache

    parameters
    ----------
    tracer_id : int
    model : str
    composition_sums : {'A': {'X': pd.DataFrame, 'Y': pd.DataFrame},
                        'Z': {'X': pd.DataFrame, 'Y': pd.DataFrame}}
    verbose : bool
    """
    for group, types in composition_sums.items():
        for composition_type, table in types.items():
            table_name = network.sums_table_name(composition_type, group_by=group)

            save_table_cache(table, tracer_id=tracer_id, model=model,
                             table_name=table_name, verbose=verbose)


def load_composition_sums_cache(tracer_id, model, verbose=True):
    """Load composition sum tables from cache

    Returns : {'A': {'X': pd.DataFrame, 'Y': pd.DataFrame},
               'Z': {'X': pd.DataFrame, 'Y': pd.DataFrame}}

    parameters
    ----------
    tracer_id : int
    model : str
    verbose : bool
    """
    sums = {'A': {}, 'Z': {}}

    for group in sums:
        for composition_type in ['X', 'Y']:
            table_name = network.sums_table_name(composition_type, group_by=group)

            table = load_table_cache(tracer_id=tracer_id, model=model,
                                     table_name=table_name, verbose=verbose)
            sums[group][composition_type] = table

    return sums


# ===============================================================
#              STIR files
# ===============================================================
def load_stir_tracer(tracer_id, model):
    """Load STIR model used for SkyNet input

    Return pd.DataFrame

    parameters
    ----------
    tracer_id : int
    model : str
    """
    filepath = paths.stir_filepath(tracer_id, model=model)
    table = pd.read_csv(filepath, header=None, skiprows=2, delim_whitespace=True)
    table.columns = tables_config.stir_columns
    return table


def get_stir_mass_grid(tracer_ids, model):
    """Get full mass grid from stir tracer files

    parameters
    ----------
    tracer_ids : int or [int]
    model : str
    """
    tracer_ids = tools.expand_sequence(tracer_ids)
    mass_grid = []

    for tracer_id in tracer_ids:
        mass = get_stir_mass_element(tracer_id, model)
        mass_grid += [mass]

    return np.array(mass_grid)


def get_stir_mass_element(tracer_id, model):
    """Get mass element (Msun) from STIR tracer file

    parameters
    ----------
    tracer_id : int
    model : str
    """
    filepath = paths.stir_filepath(tracer_id, model)
    with open(filepath, 'r') as f:
        line = f.readline()
        mass = float(line.split()[3])

    return mass


# ===============================================================
#              Cache
# ===============================================================
def save_table_cache(table, tracer_id, model, table_name, verbose=True):
    """Save tracer table to file

    parameters
    ----------
    table : pd.DataFrame
    tracer_id : int
    model : str
    table_name : one of ('columns', 'X', 'Y', 'network')
    verbose : bool
    """
    check_cache_path(model, verbose=verbose)
    filepath = paths.tracer_cache_filepath(tracer_id, model, table_name=table_name)
    printv(f'Saving table to cache: {filepath}', verbose)
    table.to_pickle(filepath)


def load_table_cache(tracer_id, model, table_name, verbose=True):
    """Load columns table from pre-cached file

    parameters
    ----------
    tracer_id : int
    model : str
    table_name : one of ('columns', 'X', 'Y', 'network')
    verbose : bool
    """
    filepath = paths.tracer_cache_filepath(tracer_id, model, table_name=table_name)
    printv(f'Loading table from cache: {filepath}', verbose)
    return pd.read_pickle(filepath)


def check_cache_path(model, verbose=True):
    """Check that the model cache directory exists
    """
    path = paths.tracer_cache_path(model)
    paths.try_mkdir(path, skip=True, verbose=verbose)
