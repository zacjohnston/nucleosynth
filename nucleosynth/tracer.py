# nucleosynth
from . import paths
from . import network
from . import load_save

"""
Class representing an individual mass tracer from a model
"""


class Tracer:
    """
    Object representing an individual mass tracer from a skynet model
    """
    def __init__(self, tracer, model, verbose=True):
        """
        parameters
        ----------
        tracer : int
        model : str
        verbose : bool
        """
        self.tracer = tracer
        self.model = model
        self.path = paths.model_path(model=model)
        self.verbose = verbose

        self.file = None
        self.network = network.get_tracer_network(tracer, model, verbose=verbose)
        self.abu = network.get_tracer_abu(tracer, model, verbose=verbose)
        self.table = load_save.load_tracer_columns(tracer, model, verbose=verbose)

    def load_tracer_file(self):
        """Load raw tracer file
        """
        self.file = load_save.load_tracer_file(self.tracer, self.model,
                                               verbose=self.verbose)
