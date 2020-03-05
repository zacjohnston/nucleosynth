# nucleosynth
from . import paths
from . import load_save

"""
Class representing an individual mass tracer from a model
"""


class Tracer:
    """Object representing an individual mass tracer from a skynet model

    attributes
    ----------
    abu : pd.DataFrame
        Table of isotopic abundances (number fraction) versus time
    columns : pd.DataFrame
        Table of main scalar quantities (density, temperature, etc.) versus time
    file : h5py.File
        Raw hdf5 tracer output file from skynet
    model : str
        Name of the core-collapse model (typically named after the progenitor model)
    network : pd.DataFrame
        Table of isotopes used in model (name, Z, A)
    path : str
        Path to skynet model output
    tracer_id : int
        The tracer ID/index
    verbose : bool
        Option to print output
    """

    def __init__(self, tracer_id, model, load_all=True, verbose=True):
        """
        parameters
        ----------
        tracer_id : int
        model : str
        load_all : bool
        verbose : bool
        """
        self.tracer_id = tracer_id
        self.model = model
        self.path = paths.model_path(model=model)
        self.verbose = verbose

        self.file = None
        self.network = None
        self.abu = None
        self.columns = None

        if load_all:
            self.load_all()

    def load_all(self):
        """Load all tracer data
        """
        self.load_file()
        self.load_network()
        self.load_abu()
        self.load_columns()

    def load_file(self):
        """Load raw tracer file
        """
        self.file = load_save.load_tracer_file(self.tracer_id, self.model,
                                               verbose=self.verbose)

    def load_network(self):
        """Load table of network isotopes
        """
        self.network = load_save.load_tracer_network(self.tracer_id, self.model,
                                                     tracer_file=self.file,
                                                     verbose=self.verbose)

    def load_abu(self):
        """Load chemical abundance table
        """
        self.abu = load_save.load_tracer_abu(self.tracer_id, self.model,
                                             tracer_file=self.file,
                                             tracer_network=self.network,
                                             verbose=self.verbose)

    def load_columns(self):
        """Load table of scalars
        """
        self.columns = load_save.load_tracer_columns(self.tracer_id, self.model,
                                                     tracer_file=self.file,
                                                     verbose=self.verbose)
