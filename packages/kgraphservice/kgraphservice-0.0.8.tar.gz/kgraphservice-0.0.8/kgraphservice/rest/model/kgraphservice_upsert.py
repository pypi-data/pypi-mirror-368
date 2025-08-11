from typing import List

from vital_ai_vitalsigns.model.GraphObject import GraphObject

from kgraphservice.rest.model.kgraphservice_op import KGraphServiceOp


class KGraphServiceUpsert(KGraphServiceOp):

    upsert_graph_object_list: List[GraphObject]


