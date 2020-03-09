import os

"""
Functions for paths/filenames

Shell environment variables needed:
NUCLEOSYNTH
    path to this repository
SKYNET_OUTPUT
    path to skynet output directory
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
    """Return path to skynet output
    """
    try:
        path = os.environ['SKYNET_OUTPUT']
    except KeyError:
        raise EnvironmentError('Environment variable SKYNET_OUTPUT not set. '
                               'Set path to skynet output directory, e.g., '
                               "'export SKYNET_OUTPUT=${HOME}/skynet/output'")
    return path


# ===============================================================
#                      Tracers
# ===============================================================
def model_path(model):
    """Return path to model output directory

        parameters
        ----------
        model : str
        """
    path = skynet_path()
    return os.path.join(path, model)


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
    path = model_path(model)
    filename = tracer_filename(tracer_id, tracer_step)
    return os.path.join(path, filename)
