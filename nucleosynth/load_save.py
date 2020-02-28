import pandas as pd
import h5py

# nucleosynth
from . import paths

"""
Functions for loading/saving data
"""


def extract_tracer(tracer, model):
    """Load skynet tracer hdf5 file

    parameters
    ----------
    tracer : int
    model : str
    """
    filepath = paths.tracer_filepath(tracer, model=model)
    f = h5py.File(filepath, 'r')

    return f
