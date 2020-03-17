
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
    """

    def __init__(self, model, tracer_ids, tracer_steps=(1, 2)):
        """
        parameters
        ----------
        model : str
        tracer_ids : int or [int]
            list of tracers. If int: assume tracer_ids = [0..(int-1)]
        """
        self.model = model
        self.path = paths.model_path(model=model)
        self.tracer_steps = tracer_steps

        tracer_ids = tools.expand_sequence(tracer_ids)
        self.tracers = dict.fromkeys(tracer_ids)
