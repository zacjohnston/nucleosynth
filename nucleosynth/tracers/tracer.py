import numpy as np
import pandas as pd
import time
from matplotlib.widgets import Slider

# nucleosynth
from nucleosynth.tracers import load_save
from nucleosynth import paths
from nucleosynth import network
from nucleosynth import plotting
from nucleosynth import printing
from nucleosynth import tools

"""
Class representing an individual mass tracer from a model
"""


class Tracer:
    """Object representing an individual mass tracer from a skynet model

    common variables/terminology
    ----------------------------
    abu_var : 'X' or 'Y'
        mass fraction (X) and number fraction (Y)
    iso_group : 'A' or 'Z'
        nuclides of constant A (isobars) and Z (isotopes)

    attributes
    ----------
    columns : pd.DataFrame
        Table of main scalar quantities (density, temperature, etc.) versus time
    composition : {abu_var: pd.DataFrame}
        Tables of X and Y versus time
    files : h5py.File
        Raw hdf5 tracer output files from skynet
    mass : float
        mass coordinate of tracer (interior mass, Msun)
    model : str
        Name of the core-collapse model (typically named after the progenitor model)
    network : pd.DataFrame
        Table of isotopes used in model (name, Z, A)
    network_unique : {iso_group: [int]}
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
    sums : {abu_var: iso_group: pd.DataFrame}
        Y and X tables, grouped and summed over A and Z
    tables : {table_name: pd.DataFrame}
        Pointer to different tables
    time : pd.Series
        Pointer to 'time' column of self.columns
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
        self.time = None
        self.tables = None

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

        self.tables = {'columns': self.columns, 'stir': self.stir}

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
        self.time = self.columns['time']

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
    def select_composition(self, abu_var, z=None, a=None):
        """Return composition (X or Y) for given Z and/or A

        parameters
        ----------
        abu_var : 'X' or 'Y'
        z : int
            atomic number
        a : int
            atomic mass number
        """
        return network.select_composition(self.composition[abu_var],
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
                     sub_figsize=(8, 4), label=None, table_name='columns',
                     linestyle='-', marker='', sharex=True):
        """Plot column quantity versus time

        parameters
        ----------
        columns : [str]
            list of quantities to plot in subplots
        max_cols : int
            how many subplots to put side-by-side
        y_scale : 'log' or 'linear'
        x_scale : 'log' or 'linear'
        legend : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        sub_figsize : [width, height]
        label : str
        linestyle : str
        marker : str
        sharex : bool
        table_name : 'columns' or 'stir'
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
                             title=title if i == 0 else False,
                             table_name=table_name)
        return fig

    def plot_column(self, column, y_scale=None, x_scale=None,
                    ax=None, legend=False, title=True,
                    ylims=None, xlims=None, figsize=(8, 6), label=None,
                    linestyle='-', marker='', table_name='columns'):
        """Plot column quantity versus time

        parameters
        ----------
        column : str
            quantity to plot on y-axis (from Tracer.columns)
        y_scale : 'log' or 'linear'
        x_scale : 'log' or 'linear'
        ax : Axes
        legend : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        figsize : [width, height]
        label : str
        linestyle : str
        marker : str
        table_name : 'columns' or 'stir'
            which table to plot from
        """
        table = self.tables[table_name]
        self.check_columns(column, table_name)

        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)
        ax.plot(table['time'], table[column], ls=linestyle,
                marker=marker, label=label)

        plotting.set_ax_all(ax, y_var=column, x_var='time', y_scale=y_scale,
                            x_scale=x_scale, ylims=ylims, xlims=xlims, legend=legend,
                            title=title, title_str=self.title)
        return fig

    def plot_composition(self, isotopes, abu_var, y_scale=None, x_scale=None,
                         ax=None, legend=True, title=True,
                         ylims=None, xlims=None, figsize=(8, 6),
                         linestyle='-', marker=''):
        """Plot network composition versus time

        parameters
        ----------
        isotopes : [str]
            list of isotopes to plot
        abu_var : 'X' or 'Y'
        y_scale : 'log' or 'linear'
        x_scale : 'log' or 'linear'
        ax : Axes
        legend : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        figsize : [width, height]
        linestyle : str
        marker : str
        """
        table = self.composition[abu_var]
        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)

        for i, isotope in enumerate(isotopes):
            ax.plot(self.time, table[isotope], ls=linestyle,
                    marker=marker, label=isotope)

        plotting.set_ax_all(ax, y_var=abu_var, x_var='time', y_scale=y_scale,
                            x_scale=x_scale, ylims=ylims, xlims=xlims, legend=legend,
                            title=title, title_str=self.title)
        return fig

    def plot_sums(self, timestep, abu_var, iso_group, y_scale=None,
                  ax=None, legend=False, title=True,
                  ylims=None, xlims=None, figsize=(8, 6), label=None,
                  linestyle='-', marker='o'):
        """Plot composition sums

        parameters
        ----------
        timestep : int
            index of timestep to plot
        abu_var : 'X' or 'Y'
        iso_group : 'A' or 'Z'
             which iso-number to group by on x-axis
        y_scale : 'log' or 'linear'
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

        x = self.network_unique[iso_group]
        y = self.sums[iso_group][abu_var].loc[timestep]

        t = self.time[timestep]
        title_str = f"{self.title}, t={t:.3e} s"
        ax.plot(x, y, ls=linestyle, marker=marker, label=label)

        plotting.set_ax_all(ax, y_var=abu_var, x_var=iso_group, y_scale=y_scale,
                            x_scale='linear', ylims=ylims, xlims=xlims, legend=legend,
                            title=title, title_str=title_str)
        return fig

    def plot_sums_slider(self, abu_var, iso_group,
                         y_scale=None, title=True, ylims=None, xlims=None,
                         legend=False, figsize=(8, 6), linestyle='-', marker='o'):
        """Plot composition sums with interactive slider

        parameters
        ----------
        abu_var : 'X' or 'Y'
        iso_group : 'A' or 'Z'
             which iso-number to group by on x-axis
        y_scale : 'log' or 'linear'
        legend : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        figsize : [width, height]
        linestyle : str
        marker : str
        """
        fig, profile_ax, slider_ax = plotting.setup_slider_fig(figsize=figsize)
        step_min, step_max = self._get_slider_steps()

        slider = Slider(slider_ax, 'timestep', step_min, step_max,
                        valinit=step_max, valstep=1)

        self.plot_sums(step_max, abu_var=abu_var, iso_group=iso_group,
                       y_scale=y_scale, ax=profile_ax, legend=legend,
                       title=title, ylims=ylims, xlims=xlims, figsize=figsize,
                       linestyle=linestyle, marker=marker)

        def update(step):
            y = self.sums[iso_group][abu_var].loc[step]
            profile_ax.lines[0].set_ydata(y)

            t = self.time[step]
            title_str = f"{self.title}, t={t:.3e} s"
            profile_ax.set_title(title_str)

            fig.canvas.draw_idle()

        slider.on_changed(update)
        return fig, slider

    def plot_sums_all(self, timestep, abu_var, y_scale=None,
                      ax=None, legend=False, title=True,
                      ylims=None, xlims=None, figsize=(8, 6),
                      linestyle='-', marker='o'):
        """Plot all isotope composition sums

        parameters
        ----------
        timestep : int
            index of timestep to plot
        abu_var : 'X' or 'Y'
        y_scale : 'log' or 'linear'
        ax : Axes
        legend : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        figsize : [width, height]
        linestyle : str
        marker : str
        """
        fig, ax = plotting.check_ax(ax=ax, figsize=figsize)

        for z in self.network_unique['Z']:
            subnet = self.select_network(z=z)
            subcomp = self.select_composition(abu_var=abu_var, z=z)

            x = subnet['A']
            y = subcomp.loc[timestep]
            label = network.get_element_str(z=z).title()

            ax.plot(x, y, ls=linestyle, marker=marker, label=label)

        t = self.time[timestep]
        title_str = f"{self.title}, t={t:.3e} s"

        plotting.set_ax_all(ax, y_var=abu_var, x_var='A', y_scale=y_scale,
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

    def _get_slider_steps(self):
        """Return numbers of steps for slider bar
        """
        step_min = self.columns.index[0]
        step_max = self.columns.index[-1]
        return step_min, step_max

    def check_columns(self, columns, tables):
        """Check if column(s) exist in provided table(s)

        parameters
        ----------
        columns : str or [str]
        tables : str or [str]
        """
        columns = tools.ensure_sequence(columns)
        tables = tools.ensure_sequence(tables)

        for table_name in tables:
            table = self.tables[table_name]

            for column in columns:
                if column not in table:
                    raise ValueError(f"column '{column}' not in tracer table '{table_name}'")
