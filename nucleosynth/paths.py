import os

"""
Functions for paths/filenames

Shell environment variables needed:
NUCLEOSYNTH

"""


# ===============================================================
#                      Repo/meta
# ===============================================================
def repo_path():
    """Return path to progs repo
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


