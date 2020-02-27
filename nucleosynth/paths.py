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


# def progs_path():
#     """Return path to top-level directory of progenitors
#     """
#     try:
#         path = os.environ['PROGENITORS']
#     except KeyError:
#         raise EnvironmentError('Environment variable PROGENITORS not set. '
#                                'Set path to progenitors top-level directory, e.g., '
#                                "'export PROGENITORS=${HOME}/data/progenitors'")
#     return path


