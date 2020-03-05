import numpy as np
import matplotlib.pyplot as plt

"""
General functions for plotting
"""


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
    ax : Axes
    figsize : [width, height]
    """
    fig = None

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    return fig, ax


def set_ax_scales(ax, y_var=None, x_var=None, y_scale=None, x_scale=None):
    """Set axis scales (linear, log)

    parameters
    ----------
    ax : Axes
    y_var : str
    x_var : str
    y_scale : one of ('log', 'linear')
    x_scale : one of ('log', 'linear')
    """
    # if x_scale is None:
    #     x_scale = self.config['plotting']['ax_scales'].get(x_var, 'log')
    # if y_scale is None:
    #     y_scale = self.config['plotting']['ax_scales'].get(y_var, 'log')

    if x_scale is not None:
        ax.set_xscale(x_scale)
    if y_scale is not None:
        ax.set_yscale(y_scale)


def set_ax_title(ax, string, title):
    """Set axis title

    parameters
    ----------
    ax : Axes
    string : str
    title : bool
    """
    if title:
        ax.set_title(string)


def set_ax_lims(ax, xlims=None, ylims=None):
    """Set x and y axis limits

    parameters
    ----------
    ax : Axes
    xlims : [min, max]
    ylims : [min, max]
    """
    if ylims is not None:
        ax.set_ylim(ylims)
    if xlims is not None:
        ax.set_xlim(xlims)


def set_ax_legend(ax, legend, loc=None):
    """Set axis labels

    parameters
    ----------
    ax : Axes
    legend : bool
    loc : str or int
    """
    if legend:
        ax.legend(loc=loc)
