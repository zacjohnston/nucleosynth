import matplotlib.pyplot as plt

# nucleosynth
from nucleosynth import plotting


class Plotter:
    """
    Handles axis properties
    """

    def __init__(self, ax, set_all=True,
                 y_var=None, x_var=None,
                 y_scale=None, x_scale=None,
                 xlabel=None, ylabel=None,
                 xlims=None, ylims=None,
                 legend=False, legend_loc=None,
                 title=False, title_str=None,
                 figsize=None):
        """
        parameters
        ----------
        ax : pyplot Axis
        set_all : bool
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
        figsize : []
        """
        self.fig = None
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
        self.figsize = figsize

        self.check_ax()

        if set_all:
            self.set_all()

    def check_ax(self):
        if self.ax is None:
            self.fig, self.ax = plt.subplots(figsize=self.figsize)

    def set_all(self):
        self.set_labels()
        self.set_legend()
        self.set_lims()
        self.set_scales()
        self.set_title()

    def set_scales(self):
        plotting.set_ax_scales(self.ax, y_var=self.y_var, x_var=self.x_var,
                               y_scale=self.y_scale, x_scale=self.x_scale)

    def set_labels(self):
        plotting.set_ax_labels(self.ax, x_var=self.x_var, y_var=self.y_var,
                               xlabel=self.xlabel, ylabel=self.ylabel)

    def set_lims(self):
        plotting.set_ax_lims(self.ax, x_var=self.x_var, y_var=self.y_var,
                             xlims=self.xlims, ylims=self.ylims)

    def set_title(self):
        plotting.set_ax_title(self.ax, string=self.title_str, title=self.title)

    def set_legend(self):
        plotting.set_ax_legend(self.ax, legend=self.legend, loc=self.legend_loc)
