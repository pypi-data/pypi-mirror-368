from vital_ai_vitalsigns.query.result_list import ResultList

from kgraphservice.kgraph_service import KGraphService
from kgraphservice.query.construct_query import ConstructQuery


class FrameQueryExecutor:

    @classmethod
    def execute_construct_query(cls,
                                kgraph_service: KGraphService,
                                graph_uri: str,
                                construct_query: ConstructQuery) -> ResultList:

        pass
