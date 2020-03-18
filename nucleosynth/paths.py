import os
import sys
import subprocess

# nucleosynth
from nucleosynth.printing import printv


"""
Functions for paths/filenames

Shell environment variables needed:
NUCLEOSYNTH
    path to this repository
SKYNET
    path to skynet directory containing input/output folders
"""


# ===============================================================
#                      Repo/meta
# ===============================================================
def repo_path():
    """Return path to nucleosynth (this) repo
    """
    try:
        path = os.environ['NUCLEOSYNTH']
    except KeyError:
        raise EnvironmentError('Environment variable NUCLEOSYNTH not set. '
                               'Set path to nucleosynth repo directory, e.g., '
                               "'export NUCLEOSYNTH=${HOME}/codes/nucleosynth'")
    return path


def skynet_path():
    """Return path to skynet directory
    """
    try:
        path = os.environ['SKYNET']
    except KeyError:
        raise EnvironmentError('Environment variable SKYNET not set. '
                               'Set path to skynet directory, e.g., '
                               "'export SKYNET=${HOME}/skynet'")
    return path


# ===============================================================
#                      Models
# ===============================================================
def get_model_paths(model):
    """Get paths to various model directories

    parameters
    ----------
    model : str
    """
    paths = {'output': model_path(model, directory='output'),
             'input':  model_path(model, directory='input'),
             'cache':  model_cache_path(model)}

    return paths


def model_path(model, directory):
    """Return path to model output directory

    parameters
    ----------
    model : str
    directory : ('input', 'output')
    """
    path = skynet_path()
    return os.path.join(path, directory, model)


# ===============================================================
#                      Tracers
# ===============================================================
def tracer_filename(tracer_id, tracer_step):
    """Return name of skynet tracer file

    parameters
    ----------
    tracer_id : int
        ID/index of tracer
    tracer_step : 1 or 2
        the skynet step/stage (1st follows STIR, 2nd is free expansion)
    """
    extensions = {1: '', 2: '_2'}
    extension = extensions[tracer_step]
    return f'{tracer_id}{extension}.h5'


def tracer_filepath(tracer_id, tracer_step, model):
    """Return path to skynet tracer file

    parameters
    ----------
    tracer_id : int
    tracer_step : 1 or 2
    model : str
    """
    path = model_path(model, directory='output')
    filename = tracer_filename(tracer_id, tracer_step)
    return os.path.join(path, filename)


# ===============================================================
#                      STIR
# ===============================================================
def stir_filename(tracer_id, model, extension='.dat'):
    """Return name of STIR tracer file
    """
    return f'{model}_{tracer_id}{extension}'


def stir_filepath(tracer_id, model):
    """Return filepath to STIR tracer
    """
    path = model_path(model, directory='input')
    filename = stir_filename(tracer_id, model)
    return os.path.join(path, filename)


# ===============================================================
#                      Cache
# ===============================================================
def model_cache_path(model):
    """Return path to temporary cache directory

    parameters
    ----------
    model : str
        """
    path = repo_path()
    return os.path.join(path, 'cache', model)


def cache_filename(tracer_id, model, table_name):
    """Return filename of columns cache

    parameters
    ----------
    tracer_id : int
    model : str
    table_name : one of ('columns', 'abu', 'mass_frac', 'network')
    """
    return f'{table_name}_{model}_tracer_{tracer_id}.pickle'


def cache_filepath(tracer_id, model, table_name):
    """Return filename of columns cache

    parameters
    ----------
    tracer_id : int
    model : str
    table_name : one of ('columns', 'abu', 'mass_frac', 'network')
    """
    path = model_cache_path(model)
    filename = cache_filename(tracer_id, model, table_name=table_name)
    return os.path.join(path, filename)


# ===============================================================
#              Misc.
# ===============================================================
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

