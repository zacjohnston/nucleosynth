# nucleosynth
from . import load_save

"""
Functions for managing nuclear network data
"""


def get_network(tracer, model):
    """Load isotope info (Z, A) from tracer

    parameters
    ----------
    tracer : int
    model : str
    """
    return load_save.load_network(tracer, model)
