
# nucleosynth
from nucleosynth.tracers import tracer
from nucleosynth import paths, tools, plotting

"""
Class representing a CCSN model, composed of multiple mass tracers
"""


class Model:
    """Object representing a CCSN model, composed of multiple mass tracers

    attributes
    ----------
    model : str
        Name of skynet model, e.g. 'traj_s12.0'
    output_path : str
        Path to skynet output directory of model
    tracers : {tracer_id: Tracer}
        Collection of tracer objects
    tracer_steps : [int]
        list of skynet "steps" making up full tracer evolution
    reload : bool
    save : bool
    """

    def __init__(self, model, tracer_ids, tracer_steps=(1, 2),
                 reload=False, save=True, verbose=True, load_all=True):
        """
        parameters
        ----------
        model : str
        tracer_ids : int or [int]
            list of tracers. If int: assume tracer_ids = [0..(int-1)]
        tracer_steps : [int]
        reload : bool
        save : bool
        verbose : bool
        """
        self.model = model
        self.output_path = paths.model_path(model, directory='output')
        self.tracer_steps = tracer_steps
        self.reload = reload
        self.save = save
        self.verbose = verbose

        tracer_ids = tools.expand_sequence(tracer_ids)
        self.tracers = dict.fromkeys(tracer_ids)

        if load_all:
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

    def load_tracers(self):
        """Load all tracers
        """
        for tracer_id in self.tracers:
            self.load_tracer(tracer_id)

    def load_tracer(self, tracer_id):
        """Load all tracers
        """
        self.tracers[tracer_id] = tracer.Tracer(tracer_id, self.model,
                                                steps=self.tracer_steps,
                                                save=self.save, reload=self.reload,
                                                verbose=self.verbose)

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
