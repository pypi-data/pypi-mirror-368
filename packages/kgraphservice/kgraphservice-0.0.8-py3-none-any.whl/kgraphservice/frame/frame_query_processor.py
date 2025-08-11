from typing import TypeVar, List, Dict

from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.query.result_list import ResultList

from kgraphservice.kgraph_service import KGraphService


G = TypeVar('G', bound='GraphObject')


class FrameQueryProcessor:

    @classmethod
    def frame_uri_query(cls, kgraph_service: KGraphService, result_list: ResultList) -> List[G]:
        pass

    @classmethod
    def frame_uri_list_query(cls, kgraph_service: KGraphService, result_list: ResultList) -> Dict[str, List[G]]:
        pass

    @classmethod
    def frame_id_query(cls, kgraph_service: KGraphService, result_list: ResultList) -> List[G]:
        pass

    @classmethod
    def frame_id_list_query(cls, kgraph_service: KGraphService, result_list: ResultList) -> Dict[str, List[G]]:
        pass

    @classmethod
    def frame_criteria_query(cls, kgraph_service: KGraphService, result_list: ResultList) -> Dict[str, List[G]]:
        pass

    