import numpy as np
import matplotlib.pyplot as plt

# nucleosynth
from .config import plot_config

"""
General functions for plotting
"""


class Plotter:
    """
    Handles axis properties
    """
    def __init__(self, ax, y_var=None, x_var=None, y_scale=None, x_scale=None,
                 xlabel=None, ylabel=None, xlims=None, ylims=None,
                 legend=False, legend_loc=None, title=False, title_str=None):
        """
        parameters
        ----------
        ax : pyplot Axis
        y_var : str
        x_var : str
        y_scale : one of ('log', 'linear')
        x_scale : one of ('log', 'linear')
        xlabel : str
        ylabel : str
        xlims : [min, max]
        ylims : [min, max]
        legend : bool
        legend_loc : str
        title : bool
        title_str : str
        """
        self.ax = ax
        self.y_var = y_var
        self.x_var = x_var
        self.y_scale = y_scale
        self.x_scale = x_scale
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xlims = xlims
        self.ylims = ylims
        self.legend = legend
        self.legend_loc = legend_loc
        self.title = title
        self.title_str = title_str

    def set_scales(self):
        set_ax_scales(self.ax, y_var=self.y_var, x_var=self.x_var,
                      y_scale=self.y_scale, x_scale=self.x_scale)

    def set_labels(self):
        set_ax_labels(self.ax, x_var=self.x_var, y_var=self.y_var,
                      xlabel=self.xlabel, ylabel=self.ylabel)

    def set_lims(self):
        set_ax_lims(self.ax, x_var=self.x_var, y_var=self.y_var,
                    xlims=self.xlims, ylims=self.ylims)

    def set_title(self):
        set_ax_title(self.ax, string=self.title_str, title=self.title)

    def set_legend(self):
        set_ax_legend(self.ax, legend=self.legend, loc=self.legend_loc)


def setup_subplots(n_sub, max_cols=2, sub_figsize=(6, 5), **kwargs):
    """Constructs fig for given number of subplots

    returns : fig, ax

    parameters
    ----------
    n_sub : int
        number of subplots (axes)
    max_cols : int
        maximum number of columns to arange subplots
    sub_figsize : tuple
        figsize of each subplot
    **kwargs :
        args to be parsed to plt.subplots()
    """
    n_rows = int(np.ceil(n_sub / max_cols))
    n_cols = {False: 1, True: max_cols}.get(n_sub > 1)
    figsize = (n_cols * sub_figsize[0], n_rows * sub_figsize[1])

    return plt.subplots(n_rows, n_cols, figsize=figsize, **kwargs)


def check_ax(ax, figsize):
    """Setup fig, ax if ax is not provided

    parameters
    ----------
    ax : pyplot Axis
    figsize : [width, height]
    """
    fig = None

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    return fig, ax


def set_ax_all(ax, y_var=None, x_var=None, y_scale=None, x_scale=None,
               xlabel=None, ylabel=None, xlims=None, ylims=None,
               legend=False, legend_loc=None, title=False, title_str=None):
    """Set all ax properties

    parameters
    ----------
    ax : pyplot Axis
    y_var : str
    x_var : str
    y_scale : one of ('log', 'linear')
    x_scale : one of ('log', 'linear')
    xlabel : str
    ylabel : str
    xlims : [min, max]
    ylims : [min, max]
    legend : bool
    legend_loc : str
    title : bool
    title_str : str
    """
    set_ax_scales(ax, x_var=x_var, y_var=y_var, x_scale=x_scale, y_scale=y_scale)
    set_ax_labels(ax, y_var=y_var, x_var=x_var, ylabel=ylabel, xlabel=xlabel)
    set_ax_lims(ax, x_var=x_var, y_var=y_var, xlims=xlims, ylims=ylims)
    set_ax_legend(ax, legend=legend, loc=legend_loc)
    set_ax_title(ax, string=title_str, title=title)


def set_ax_scales(ax, y_var=None, x_var=None, y_scale=None, x_scale=None):
    """Set axis scales (linear, log)

    parameters
    ----------
    ax : pyplot Axis
    y_var : str
    x_var : str
    y_scale : one of ('log', 'linear')
    x_scale : one of ('log', 'linear')
    """
    if x_scale is None:
        x_scale = plot_config.ax_scales.get(x_var, 'linear')
    if y_scale is None:
        y_scale = plot_config.ax_scales.get(y_var, 'log')

    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)


def set_ax_title(ax, string, title):
    """Set axis title

    parameters
    ----------
    ax : pyplot Axis
    string : str
    title : bool
    """
    if title:
        ax.set_title(string)


def set_ax_lims(ax, x_var=None, y_var=None, xlims=None, ylims=None):
    """Set x and y axis limits

    parameters
    ----------
    ax : pyplot Axis
    x_var : str
    y_var : str
    xlims : [min, max]
    ylims : [min, max]
    """
    if xlims is None:
        xlims = plot_config.ax_lims.get(x_var)
    if ylims is None:
        ylims = plot_config.ax_lims.get(y_var)

    ax.set_xlim(xlims)
    ax.set_ylim(ylims)


def set_ax_labels(ax, x_var=None, y_var=None, xlabel=None, ylabel=None):
    """Set x and y axis limits

    parameters
    ----------
    ax : pyplot Axis
    x_var : str
    y_var : str
    xlabel : str
    ylabel : str
    """
    if ylabel is None:
        ylabel = plot_config.ax_labels.get(y_var, y_var)
    if xlabel is None:
        xlabel = plot_config.ax_labels.get(x_var, x_var)

    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)


def set_ax_legend(ax, legend, loc=None):
    """Set axis labels

    parameters
    ----------
    ax : pyplot Axis
    legend : bool
    loc : str or int
    """
    if legend:
        ax.legend(loc=loc)
