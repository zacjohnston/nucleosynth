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
    abu : pd.DataFrame
        Table of isotopic abundances (Y, number fraction) versus time
    columns : pd.DataFrame
        Table of main scalar quantities (density, temperature, etc.) versus time
    files : h5py.File
        Raw hdf5 tracer output files from skynet
    mass : float
        mass of tracer (Msun)
    mass_frac : pd.DataFrame
        Table of isotopic mass fractions (X) versus time
    model : str
        Name of the core-collapse model (typically named after the progenitor model)
    network : pd.DataFrame
        Table of isotopes used in model (name, Z, A)
    network_unique : {group: [int]}
        unique A and Z in network
    path : str
        Path to skynet model output
    reload : bool
        whether to force reload from raw file (i.e. don't load cache)
    save : bool
        whether to save tables to cache for faster loading
    steps : [int]
        list of skynet model steps
    sums : {table: group: pd.DataFrame}
        abundance/mass fraction tables, grouped and summed over A/Z
    tracer_id : int
        The tracer ID/index
    verbose : bool
        Option to print output
    """

    def __init__(self, tracer_id, model, load_all=True,
                 steps=(1, 2), mass=0.01,
                 save=True, reload=False, verbose=True):
        """
        parameters
        ----------
        tracer_id : int
        model : str
        steps : [int]
        load_all : bool
        mass : float
        save : bool
        reload : bool
        verbose : bool
        """
        self.tracer_id = tracer_id
        self.model = model
        self.path = paths.model_path(model=model)
        self.mass = mass
        self.verbose = verbose
        self.steps = steps
        self.save = save
        self.reload = reload

        self.files = None
        self.network = None
        self.abu = None
        self.mass_frac = None

        self.network_unique = None
        self.sums = None

        self.columns = None
        self.title = f'{self.model}, tracer_{self.tracer_id}'

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

        self.load_mass_frac()
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

        if self.columns is None:
            self.load_columns()

        if self.network is None:
            self.load_network()

        if self.abu is None:
            self.load_abu()

    def load_files(self):
        """Load raw tracer files
        """
        self.files = load_save.load_files(self.tracer_id,
                                          tracer_steps=self.steps,
                                          model=self.model,
                                          verbose=self.verbose)

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
        self.network_unique = {}
        for group in ['A', 'Z']:
            self.network_unique[group] = np.unique(self.network[group])

    def load_abu(self):
        """Load chemical abundance table
        """
        self.printv('Loading abundances')
        self.abu = load_save.load_table(self.tracer_id, tracer_steps=self.steps,
                                        model=self.model,
                                        tracer_files=self.files,
                                        table_name='abu',
                                        tracer_network=self.network,
                                        save=self.save, reload=self.reload,
                                        verbose=False)

    def load_mass_frac(self):
        """Get mass fraction (X) table from abu table
        """
        self.printv('Loading mass fractions')
        self.check_loaded()
        self.mass_frac = load_save.load_table(self.tracer_id, model=self.model,
                                              table_name='mass_frac',
                                              tracer_steps=self.steps,
                                              tracer_files=self.files,
                                              tracer_network=self.network,
                                              abu_table=self.abu,
                                              reload=self.reload, save=self.save,
                                              verbose=False)

    def load_sums(self):
        """Get abundance/mass-fraction sums over A, Z
        """
        self.printv('Calculating composition sums')
        self.check_loaded()
        self.sums = {'abu': {}, 'mass_frac': {}}
        tables = {'abu': self.abu, 'mass_frac': self.mass_frac}

        for group in ['A', 'Z']:
            for key, table in tables.items():
                self.sums[key][group] = network.get_table_sums(table, self.network, group)

    def load_sumy_abar(self):
        """Get sumY and Abar versus time from abu table
        """
        self.check_loaded()
        self.columns['sumy'] = network.get_sumy(self.abu)
        self.columns['abar'] = 1 / self.columns['sumy']

    def get_zbar(self):
        """Get Zbar versus time from abu table
        """
        self.check_loaded()
        self.columns['zbar'] = network.get_zbar(self.abu, self.network,
                                                ye=self.columns['ye'])

    # ===============================================================
    #                      Accessing Data
    # ===============================================================
    def get_abu(self, z=None, a=None):
        """Return abundance column(s) for given Z and/or A

        z : int
            atomic number
        a : int
            atomic mass number
        """
        return network.select_table(self.abu, tracer_network=self.network, z=z, a=a)

    def get_network(self, z=None, a=None):
        """Return subset of network with given Z and/or A

        z : int
            atomic number
        a : int
            atomic mass number
        """
        return network.select_network(self.network, z=z, a=a)

    # ===============================================================
    #                      Plotting
    # ===============================================================
    def plot(self, column, y_scale=None, x_scale=None,
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
        # TODO: plot multiple subplots
        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)

        ax.plot(self.columns['time'], self.columns[column], ls=linestyle,
                marker=marker, label=label)

        plotting.set_ax_all(ax, y_var=column, x_var='time', y_scale=y_scale,
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
        table : one of ['abu', 'mass_frac']
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
        y = self.sums[table][group].loc[timestep]

        time = self.columns['time'][timestep]
        title_str = f"{self.title}, t={time:.3e} s"
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
