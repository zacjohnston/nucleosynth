import numpy as np
import pandas as pd
import time

# nucleosynth
from nucleosynth.tracers import load_save
from nucleosynth import paths
from nucleosynth import network
from nucleosynth import plotting
from nucleosynth import printing

"""
Class representing an individual mass tracer from a model
"""


class Tracer:
    """Object representing an individual mass tracer from a skynet model

    attributes
    ----------
    columns : pd.DataFrame
        Table of main scalar quantities (density, temperature, etc.) versus time
    composition : {'Y': pd.DataFrame, 'X': pd.DataFrame}
        Tables of isotopic number fractions (Y) and mass fractions (X) versus time
    files : h5py.File
        Raw hdf5 tracer output files from skynet
    mass : float
        mass coordinate of tracer (interior mass, Msun)
    model : str
        Name of the core-collapse model (typically named after the progenitor model)
    network : pd.DataFrame
        Table of isotopes used in model (name, Z, A)
    network_unique : {group: [int]}
        unique A and Z in network
    paths : str
        Paths to model input/output directories
    reload : bool
        whether to force reload from raw file (i.e. don't load cache)
    save : bool
        whether to save tables to cache for faster loading
    steps : [int]
        list of skynet model steps
    stir : pd.DataFrame
        tracer input taken from STIR model
    sums : {table: group: pd.DataFrame}
        Y and X tables, grouped and summed over A and Z
    tracer_id : int
        The tracer ID/index
    verbose : bool
        Option to print output
    """

    def __init__(self, tracer_id, model, load_all=True,
                 steps=(1, 2), save=True, reload=False,
                 verbose=True):
        """
        parameters
        ----------
        tracer_id : int
        model : str
        steps : [int]
        load_all : bool
        save : bool
        reload : bool
        verbose : bool
        """
        self.tracer_id = tracer_id
        self.model = model
        self.verbose = verbose
        self.steps = steps
        self.save = save
        self.reload = reload

        self.files = None
        self.network = None
        self.composition = None
        self.network_unique = None
        self.sums = None
        self.columns = None
        self.stir = None

        self.mass = load_save.get_stir_mass_element(tracer_id, self.model)
        self.title = f'{self.model}, tracer_{self.tracer_id}'
        self.paths = paths.get_model_paths(self.model)

        if load_all:
            self.load_all()

    # ===============================================================
    #                      Loading/extracting
    # ===============================================================
    def load_all(self):
        """Load all tracer data
        """
        t0 = time.time()
        self.check_loaded()

        self.load_sums()
        self.load_sumy_abar()
        self.get_zbar()

        t1 = time.time()
        self.printv(f'Load time: {t1-t0:.3f} s')

    def check_loaded(self):
        """Check that main data is loaded
        """
        if self.files is None:
            self.load_files()

        if self.stir is None:
            self.load_stir()

        if self.columns is None:
            self.load_columns()

        if self.network is None:
            self.load_network()

        if self.composition is None:
            self.load_composition()

    def load_files(self):
        """Load raw tracer files
        """
        self.files = load_save.load_files(self.tracer_id,
                                          tracer_steps=self.steps,
                                          model=self.model,
                                          verbose=self.verbose)

    def load_stir(self):
        """Load stir tracer table
        """
        self.printv('Loading stir tracer')
        self.stir = load_save.load_stir_tracer(self.tracer_id, model=self.model)

    def load_columns(self):
        """Load table of scalars
        """
        self.printv('Loading columns')
        self.columns = load_save.load_table(self.tracer_id,
                                            model=self.model,
                                            tracer_steps=self.steps,
                                            table_name='columns',
                                            tracer_files=self.files,
                                            save=self.save, reload=self.reload,
                                            verbose=False)

    def load_network(self):
        """Load table of network isotopes
        """
        self.printv('Loading network')
        self.network = load_save.load_table(self.tracer_id,
                                            model=self.model,
                                            tracer_steps=self.steps,
                                            table_name='network',
                                            tracer_files=self.files,
                                            save=self.save, reload=self.reload,
                                            verbose=False)
        self.get_network_unique()

    def get_network_unique(self):
        """Get unique Z and A in network
        """
        self.network_unique = network.get_network_unique(self.network)

    def load_composition(self):
        """Load composition tables (X, Y)
        """
        self.printv('Loading composition tables')
        self.composition = load_save.load_composition(self.tracer_id,
                                                      tracer_steps=self.steps,
                                                      model=self.model,
                                                      tracer_files=self.files,
                                                      tracer_network=self.network,
                                                      reload=self.reload,
                                                      save=self.save,
                                                      verbose=False)

    def load_sums(self):
        """Get X, Y sums over A, Z
        """
        self.printv('Loading composition sums')
        self.sums = load_save.load_sums(self.tracer_id,
                                        tracer_steps=self.steps,
                                        model=self.model,
                                        tracer_files=self.files,
                                        tracer_network=self.network,
                                        reload=self.reload,
                                        save=self.save,
                                        verbose=False)

    def load_sumy_abar(self):
        """Get sumY and Abar versus time from Y table
        """
        self.check_loaded()
        self.columns['sumy'] = network.get_sumy(self.composition['Y'])
        self.columns['abar'] = 1 / self.columns['sumy']

    def get_zbar(self):
        """Get Zbar versus time from Y table
        """
        self.check_loaded()
        self.columns['zbar'] = network.get_zbar(self.composition['Y'],
                                                self.network,
                                                ye=self.columns['ye'])

    # ===============================================================
    #                      Accessing Data
    # ===============================================================
    def select_composition(self, key, z=None, a=None):
        """Return composition (X or Y) for given Z and/or A

        parameters
        ----------
        key : one of ('X', 'Y')
        z : int
            atomic number
        a : int
            atomic mass number
        """
        return network.select_composition(self.composition[key],
                                          tracer_network=self.network, z=z, a=a)

    def select_network(self, z=None, a=None):
        """Return subset of network with given Z and/or A

        parameters
        ----------
        z : int
            atomic number
        a : int
            atomic mass number
        """
        return network.select_isotopes(self.network, z=z, a=a)

    # ===============================================================
    #                      Plotting
    # ===============================================================
    def plot_columns(self, columns, max_cols=1, y_scale=None, x_scale=None,
                     legend=False, title=True, ylims=None, xlims=None,
                     sub_figsize=(8, 4), label=None,
                     linestyle='-', marker='', sharex=True):
        """Plot column quantity versus time

        parameters
        ----------
        columns : [str]
            list of quantities to plot in subplots
        max_cols : int
            how many subplots to put side-by-side
        y_scale : {'log', 'linear'}
        x_scale : {'log', 'linear'}
        legend : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        sub_figsize : [width, height]
        label : str
        linestyle : str
        marker : str
        sharex : bool
        """
        fig, ax = plotting.setup_subplots(n_sub=len(columns), max_cols=max_cols,
                                          sub_figsize=sub_figsize,
                                          sharex=sharex, squeeze=False)

        for i, column in enumerate(columns):
            row = int(np.floor(i / max_cols))
            col = i % max_cols

            self.plot_column(column, ax=ax[row, col], y_scale=y_scale, x_scale=x_scale,
                             ylims=ylims, xlims=xlims, label=label,
                             legend=legend, linestyle=linestyle, marker=marker,
                             title=title if i == 0 else False)
        return fig

    def plot_column(self, column, y_scale=None, x_scale=None,
                    ax=None, legend=False, title=True,
                    ylims=None, xlims=None, figsize=(8, 6), label=None,
                    linestyle='-', marker=''):
        """Plot column quantity versus time

        parameters
        ----------
        column : str
            quantity to plot on y-axis (from Tracer.columns)
        y_scale : {'log', 'linear'}
        x_scale : {'log', 'linear'}
        ax : Axes
        legend : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        figsize : [width, height]
        label : str
        linestyle : str
        marker : str
        """
        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)

        ax.plot(self.columns['time'], self.columns[column], ls=linestyle,
                marker=marker, label=label)

        plotting.set_ax_all(ax, y_var=column, x_var='time', y_scale=y_scale,
                            x_scale=x_scale, ylims=ylims, xlims=xlims, legend=legend,
                            title=title, title_str=self.title)
        return fig

    def plot_composition(self, isotopes, table_name, y_scale=None, x_scale=None,
                         ax=None, legend=True, title=True,
                         ylims=None, xlims=None, figsize=(8, 6),
                         linestyle='-', marker=''):
        """Plot network composition versus time

        parameters
        ----------
        isotopes : [str]
            list of isotopes to plot
        table_name : one of ('Y', 'X')
            which composition quantity to plot
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
        table = self.composition[table_name]
        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)

        for i, isotope in enumerate(isotopes):
            ax.plot(self.columns['time'], table[isotope], ls=linestyle,
                    marker=marker, label=isotope)

        plotting.set_ax_all(ax, y_var=table_name, x_var='time', y_scale=y_scale,
                            x_scale=x_scale, ylims=ylims, xlims=xlims, legend=legend,
                            title=title, title_str=self.title)
        return fig

    def plot_sums(self, timestep, table, group, y_scale=None,
                  ax=None, legend=False, title=True,
                  ylims=None, xlims=None, figsize=(8, 6), label=None,
                  linestyle='-', marker='o'):
        """Plot composition sums versus time

        parameters
        ----------
        timestep : int
            index of timestep to plot
        table : one of ['Y', 'X']
             which composition table to plot
        group : one of ['A', 'Z']
             which atomic number to group by on x-axis
        y_scale : {'log', 'linear'}
        ax : Axes
        legend : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        figsize : [width, height]
        label : str
        linestyle : str
        marker : str
        """
        # TODO: slider for timestep
        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)

        x = self.network_unique[group]
        y = self.sums[group][table].loc[timestep]

        t = self.columns['time'][timestep]
        title_str = f"{self.title}, t={t:.3e} s"
        ax.plot(x, y, ls=linestyle, marker=marker, label=label)

        plotting.set_ax_all(ax, y_var=table, x_var=group, y_scale=y_scale,
                            x_scale='linear', ylims=ylims, xlims=xlims, legend=legend,
                            title=title, title_str=title_str)
        return fig

    # ===============================================================
    #                      Convenience
    # ===============================================================
    def printv(self, string):
        """Print string if verbose is True
        """
        printing.printv(string, verbose=self.verbose)
