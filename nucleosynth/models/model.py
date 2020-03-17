
# nucleosynth
from nucleosynth.tracers import tracer
from nucleosynth import paths

"""
Class representing a CCSN model, composed of multiple mass tracers
"""


class Model:
    """Object representing a CCSN model, composed of multiple mass tracers

    attributes
    ----------
    model : str
    path : str
    """
    def __init__(self, model):
        """
        parameters
        ----------
        model : str
        """
        self.model = model
        self.path = paths.model_path(model=model)
