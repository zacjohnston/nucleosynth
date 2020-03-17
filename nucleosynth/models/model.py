
# nucleosynth
from nucleosynth.tracers import tracer
from nucleosynth import paths, tools

"""
Class representing a CCSN model, composed of multiple mass tracers
"""


class Model:
    """Object representing a CCSN model, composed of multiple mass tracers

    attributes
    ----------
    model : str
        Name of skynet model, e.g. 'traj_s12.0'
    path : str
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
        self.path = paths.model_path(model=model)
        self.tracer_steps = tracer_steps
        self.reload = reload
        self.save = save
        self.verbose = verbose

        tracer_ids = tools.expand_sequence(tracer_ids)
        self.tracers = dict.fromkeys(tracer_ids)

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

