from kgraphservice.rest.model.kgraphservice_op import KGraphServiceOp


class KGraphServiceFrameDelete(KGraphServiceOp):

    graph_uri: str
    frame_uri: str


