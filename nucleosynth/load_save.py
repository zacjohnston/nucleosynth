import numpy as np
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
    table = pd.DataFrame()
    f = load_hdf5(tracer, model)
    keys = ['Time', 'Density', 'Temperature', 'Ye', 'HeatingRate', 'Entropy']

    for key in keys:
        table[key.lower()] = f[key]

    return table


def load_network(tracer, model):
    """Load isotope info (Z, A) for tracer

    parameters
    ----------
    tracer : int
    model : str
    """
    table = pd.DataFrame()
    f = load_hdf5(tracer, model)

    for key in ['Z', 'A']:
        table[key] = np.array(f[key], dtype=int)

    return table


def load_hdf5(tracer, model):
    """Load skynet tracer hdf5 file

    parameters
    ----------
    tracer : int
    model : str
    """
    filepath = paths.tracer_filepath(tracer, model=model)
    f = h5py.File(filepath, 'r')

    return f
