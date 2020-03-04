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
        self.network = None
        self.abu = None
        self.table = None

    def load_file(self):
        """Load raw tracer file
        """
        self.file = load_save.load_tracer_file(self.tracer, self.model,
                                               verbose=self.verbose)

    def load_network(self):
        """Load network of isotopes
        """
        self.network = network.get_tracer_network(self.tracer, self.model, self.verbose)

    def load_abu(self):
        """Load chemical abundances
        """
        self.abu = network.get_tracer_abu(self.tracer, self.model, self.verbose)

    def load_table(self):
        """Load table of scalars
        """
        self.table = load_save.load_tracer_columns(self.tracer, self.model,
                                                   tracer_file=self.file,
                                                   verbose=self.verbose)
