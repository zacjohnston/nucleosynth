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
    columns : [str]
        list of column names available in tracer time-series data
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
    yields : pd.DataFrame
        final composition yields, summed over all tracers
    yield_sums : {'A': pd.DataFrame, 'Z': pd.DataFrame}
        sums over yields grouped by A and Z
    """

    def __init__(self,
                 model,
                 tracer_ids,
                 tracer_steps=(1, 2),
                 reload=False,
                 save=True,
                 load_all=True,
                 verbose=True):
        """
        parameters
        ----------
        model : str
        tracer_ids : int or [int]
            list of tracers. If int: assume tracer_ids = [0 .. (int-1)]
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
        self.yield_sums = None
        self.mass_grid = None
        self.dmass = None
        self.total_mass = None
        self.columns = None

        self.tracers = dict.fromkeys(self.tracer_ids)
        self.paths = paths.get_model_paths(self.model)

        if load_all:
            self.load_all()

    # ===============================================================
    #                      Loading/extracting
    # ===============================================================
    def load_all(self):
        """Load all data
        """
        self.load_mass_grid()
        self.load_network()
        self.load_tracers()
        self.get_columns()
        self.get_yields()
        self.get_yield_sums()

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
        self.printv('-'*20 + f'\nTotal load time: {t1-t0:.3f} s\n' + '-'*20)

    def load_tracer(self, tracer_id):
        """Load all tracers
        """
        self.tracers[tracer_id] = tracers.tracer.Tracer(tracer_id, self.model,
                                                        steps=self.tracer_steps,
                                                        save=self.save, reload=self.reload,
                                                        verbose=self.verbose)

    def get_columns(self):
        """Get list of columns in tracer data
        """
        tracer_id_0 = self.tracer_ids[0]
        self.columns = list(self.tracers[tracer_id_0].columns.columns)

    # ===============================================================
    #                      Analysis
    # ===============================================================
    def get_yields(self):
        """Sum over all tracers to obtain final composition yields
        """
        self.printv('Calculating final yields')
        self.check_loaded()
        self.yields = network.get_yields(self.tracers, tracer_network=self.network)
        self.yields['msun'] = self.yields['X'] * self.total_mass

    def get_yield_sums(self):
        """Sum over yields, grouped by A and Z
        """
        self.printv('Grouping final yields by A and Z')
        self.check_loaded()
        self.yield_sums = network.get_all_yield_sums(self.yields)

        # get mass yield in msun
        for iso_group in ['A', 'Z']:
            table = self.yield_sums[iso_group]
            table['msun'] = table['X'] * self.total_mass

    # ===============================================================
    #                      Accessing Data
    # ===============================================================
    def select_yields(self, a=None, z=None):
        """Select subset of yields matching given A and/or Z
        """
        return network.select_isotopes(self.yields, a=a, z=z)

    # ===============================================================
    #                      Plotting
    # ===============================================================
    def plot_column(self, column, tracer_ids=None, y_scale=None, x_scale=None,
                    ax=None, legend=False, ylims=None, xlims=None,
                    figsize=(8, 6), linestyle='-', marker='',
                    table_name='columns'):
        """Plot column quantity versus time

        parameters
        ----------
        column : str
            quantity to plot on y-axis (from Tracer.columns)
        tracer_ids : [int]
        y_scale : 'log' or 'linear'
        x_scale : 'log' or 'linear'
        ax : Axes
        legend : bool
        ylims : [min, max]
        xlims : [min, max]
        figsize : [width, height]
        linestyle : str
        marker : str
        table_name : one of ['columns', 'stir']
        """
        if tracer_ids is None:
            tracer_ids = self.tracers.keys()

        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)

        for tracer_id in tracer_ids:
            trace = self.tracers[tracer_id]
            mass = f'{self.mass_grid[tracer_id]:.2f}'
            trace.plot_column(column=column, ax=ax,
                              y_scale=y_scale, x_scale=x_scale, ylims=ylims, xlims=xlims,
                              legend=legend, title=False, label=mass,
                              linestyle=linestyle, marker=marker,
                              table_name=table_name)

    def plot_yield_sums(self, abu_var, iso_group, y_scale=None,
                        ax=None, legend=False, ylims=None, xlims=None,
                        figsize=(8, 6), label=None, linestyle='-', marker='o'):
        """Plot nucleosynthesis yields, grouped by A or Z

        parameters
        ----------
        abu_var : one of ['X', 'Y']
             which composition quantitiy to plot
        iso_group : one of ['A', 'Z']
             which atomic number to group by on x-axis
        y_scale : 'log' or 'linear'
        ax : Axes
        legend : bool
        ylims : [min, max]
        xlims : [min, max]
        figsize : [width, height]
        label : str
        linestyle : str
        marker : str
        """
        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)

        x = self.network_unique[iso_group]
        y = self.yield_sums[iso_group][abu_var]

        ax.plot(x, y, ls=linestyle, marker=marker, label=label)

        plotting.set_ax_all(ax, y_var=abu_var, x_var=iso_group, y_scale=y_scale,
                            x_scale='linear', ylims=ylims, xlims=xlims, legend=legend)

    # ===============================================================
    #                      Convenience
    # ===============================================================
    def printv(self, string):
        """Print string if verbose is True
        """
        printing.printv(string, verbose=self.verbose)
