
from kgraphservice.rest.model.kgraphservice_op import KGraphServiceOp


class KGraphServiceInteractionGet(KGraphServiceOp):

    graph_uri: str
    interaction_uri: str
