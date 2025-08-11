from kgraphservice.rest.model.kgraphservice_op import KGraphServiceOp


class KGraphServiceFrameGet(KGraphServiceOp):

    graph_uri: str
    frame_uri: str


