from typing import List

from kgraphservice.rest.model.kgraphservice_op import KGraphServiceOp


class KGraphServiceDelete(KGraphServiceOp):

    graph_uri: str
    delete_uri_list: List[str]

