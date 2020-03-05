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


def tracer_filename(tracer_id):
    """Return name of skynet tracer file

    parameters
    ----------
    tracer_id : int
    """
    return f'{tracer_id}.h5'


def tracer_filepath(tracer_id, model):
    """Return path to skynet tracer file

    parameters
    ----------
    tracer_id : int
    model : str
    """
    path = model_path(model)
    filename = tracer_filename(tracer_id)
    return os.path.join(path, filename)
