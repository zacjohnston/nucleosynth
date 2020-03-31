import numpy as np
import pandas as pd
import time

# nucleosynth
from nucleosynth import tracers
from nucleosynth import paths, tools, plotting, printing, network

"""
Class representing a CCSN model, composed of multiple mass tracers
"""


class Model:
    """Object representing a CCSN model, composed of multiple mass tracers

    attributes
    ----------
    model : str
        Name of skynet model, e.g. 'traj_s12.0'
    n_tracers : int
        number of tracers in model
    paths : str
        Path to skynet output directory of model
    tracers : {tracer_id: Tracer}
        Collection of tracer objects
    tracer_steps : [int]
        list of skynet "steps" making up full tracer evolution
    reload : bool
    save : bool
    """

    def __init__(self, model, tracer_ids, tracer_steps=(1, 2),
                 reload=False, save=True, load_all=True, verbose=True):
        """
        parameters
        ----------
        model : str
        tracer_ids : int or [int]
            list of tracers. If int: assume tracer_ids = [0..(int-1)]
        tracer_steps : [int]
        reload : bool
        save : bool
        load_all : bool
        verbose : bool
        """
        self.model = model
        self.tracer_ids = tools.expand_sequence(tracer_ids)
        self.n_tracers = len(self.tracer_ids)
        self.tracer_steps = tracer_steps
        self.reload = reload
        self.save = save
        self.verbose = verbose

        self.network_unique = None
        self.network = None
        self.yields = None
        self.mass_grid = None
        self.dmass = None
        self.total_mass = None

        self.tracers = dict.fromkeys(self.tracer_ids)
        self.paths = paths.get_model_paths(self.model)
        self.load_mass_grid()

        if load_all:
            self.load_network()
            self.load_tracers()

    # ===============================================================
    #                      Loading/extracting
    # ===============================================================
    def check_loaded(self):
        """Check that main data is loaded
        """
        for tracer_id in self.tracers:
            if self.tracers[tracer_id] is None:
                self.load_tracer(tracer_id)

    def load_mass_grid(self):
        """Load mass coordinate grid
        """
        self.mass_grid = tracers.load_save.get_stir_mass_grid(self.tracer_ids,
                                                              model=self.model,
                                                              verbose=self.verbose)
        self.dmass = np.diff(self.mass_grid)[0]  # Assume equally-spaced
        self.total_mass = len(self.tracers)*self.dmass

    def load_network(self):
        """Load table of network isotopes
        """
        self.printv('Loading network')
        self.network = tracers.load_save.load_table(tracer_id=self.tracer_ids[0],
                                                    model=self.model,
                                                    tracer_steps=self.tracer_steps,
                                                    table_name='network',
                                                    save=self.save, reload=self.reload,
                                                    verbose=False)
        self.get_network_unique()

    def get_network_unique(self):
        """Get unique Z and A in network
        """
        self.network_unique = network.get_network_unique(self.network)

    def load_tracers(self):
        """Load all tracers
        """
        t0 = time.time()
        for tracer_id in self.tracers:
            self.printv('-'*20)
            self.load_tracer(tracer_id)

        t1 = time.time()
        self.printv(f'Total load time: {t1-t0:.3f} s')

    def load_tracer(self, tracer_id):
        """Load all tracers
        """
        self.tracers[tracer_id] = tracers.tracer.Tracer(tracer_id, self.model,
                                                        steps=self.tracer_steps,
                                                        save=self.save, reload=self.reload,
                                                        verbose=self.verbose)

    # ===============================================================
    #                      Analysis
    # ===============================================================
    def get_final_yields(self):
        """Calculate final yields
        """
        self.check_loaded()
        self.yields = pd.DataFrame(self.network['isotope'])

        for table in ['X', 'Y']:
            self.yields[table] = 0.0

            for tracer_id, tracer in self.tracers.items():
                last_row = tracer.composition[table].iloc[-1]
                self.yields[table] += np.array(last_row) / self.n_tracers

    # ===============================================================
    #                      Plotting
    # ===============================================================
    def plot_column(self, column, tracer_ids=None, y_scale=None, x_scale=None,
                    ax=None, legend=False, title=True,
                    ylims=None, xlims=None, figsize=(8, 6),
                    linestyle='-', marker=''):
        """Plot column quantity versus time

        parameters
        ----------
        column : str
            quantity to plot on y-axis (from Tracer.columns)
        tracer_ids : [int]
        y_scale : {'log', 'linear'}
        x_scale : {'log', 'linear'}
        ax : Axes
        legend : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        figsize : [width, height]
        linestyle : str
        marker : str
        """
        if tracer_ids is None:
            tracer_ids = self.tracers.keys()

        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)

        for tracer_id in tracer_ids:
            trace = self.tracers[tracer_id]
            trace.plot_column(column=column, ax=ax,
                              y_scale=y_scale, x_scale=x_scale, ylims=ylims, xlims=xlims,
                              legend=legend, title=title, label=tracer_id,
                              linestyle=linestyle, marker=marker)

    # ===============================================================
    #                      Convenience
    # ===============================================================
    def printv(self, string):
        """Print string if verbose is True
        """
        printing.printv(string, verbose=self.verbose)



