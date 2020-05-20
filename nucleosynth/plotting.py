import numpy as np
import matplotlib.pyplot as plt

# nucleosynth
from .config import plot_config

"""
General functions for plotting
"""


def setup_subplots(n_sub, max_cols=1, sub_figsize=(6, 5), **kwargs):
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


def setup_slider_fig(figsize):
    """Setup fig, ax for slider

    parameters
    ----------
    figsize : [width, height]
    """
    fig = plt.figure(figsize=figsize)
    profile_ax = fig.add_axes([0.1, 0.2, 0.8, 0.65])
    slider_ax = fig.add_axes([0.1, 0.05, 0.8, 0.05])

    return fig, profile_ax, slider_ax


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

    ax.set_xscale(x_scale, linthreshx=10)
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
