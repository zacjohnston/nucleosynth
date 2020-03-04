
# nucleosynth
from . import paths
from . import network
from . import load_save

"""
Class representing an individual mass tracer from a model
"""


class Tracer:
    """
    Object representing an individual mass tracer from a model
    """
    def __init__(self, tracer, model):
        """
        parameters
        ----------
        tracer : int
        model : str
        """
        self.tracer = tracer
        self.model = model
        self.path = paths.model_path(model=model)

        self.network = network.get_tracer_network(tracer=tracer, model=model)
        self.abu = network.get_tracer_abu(tracer=tracer, model=model)
        self.table = load_save.extract_tracer_columns(tracer=tracer, model=model)
