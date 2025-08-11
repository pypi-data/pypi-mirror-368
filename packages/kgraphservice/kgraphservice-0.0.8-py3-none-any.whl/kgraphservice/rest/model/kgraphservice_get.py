from typing import List

from kgraphservice.rest.model.kgraphservice_op import KGraphServiceOp


class KGraphServiceGet(KGraphServiceOp):

    graph_uri: str
    get_uri_list: List[str]

