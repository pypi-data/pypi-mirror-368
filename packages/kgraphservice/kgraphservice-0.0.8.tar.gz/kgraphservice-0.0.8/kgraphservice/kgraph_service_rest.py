import json
from typing import TypeVar, Optional, List, Type, Tuple

from ai_haley_kg_domain.model.KGInteraction import KGInteraction
from ai_haley_kg_domain.model.KGNode import KGNode
from vital_ai_vitalsigns.metaql.metaql_query import SelectQuery, GraphQuery
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.query.metaql_result import MetaQLResult
from vital_ai_vitalsigns.query.part_list import PartList
from vital_ai_vitalsigns.query.result_element import ResultElement
from vital_ai_vitalsigns.query.result_list import ResultList
from vital_ai_vitalsigns.service.vital_namespace import VitalNamespace
from vital_ai_vitalsigns.service.vital_service_status import VitalServiceStatus

from kgraphservice.client.kgraphservice_client import KGraphServiceClient
from kgraphservice.inf.kgraph_service_inf import KGraphServiceInterface
from kgraphservice.info.frame_info import FrameInfo
from kgraphservice.info.interaction_info import InteractionInfo
from kgraphservice.info.kgraph_info import KGraphInfo
from kgraphservice.part.kgframe_part import KGFramePart
from kgraphservice.rest.impl.kgraphservice_builder import KGraphServiceBuilder
from kgraphservice.rest.impl.kgraphservice_parser import KGraphServiceParser

G = TypeVar('G', bound=Optional[GraphObject])
KGN = TypeVar('KGN', bound=Optional[KGNode])
KGFP = TypeVar('KGFP', bound=Optional[KGFramePart])


class KGraphServiceREST(KGraphServiceInterface):

    def __init__(self, *, host="localhost", port=6008):
        self._host = host
        self._port = port

    def get_kgraph(self, graph_uri: str) -> VitalNamespace:
        pass

    def list_kgraphs(self) -> List[VitalNamespace]:

        client = KGraphServiceClient(
            host=self._host, port=self._port
        )

        graph_list_op = KGraphServiceBuilder.build_kgraph_list_op()

        request = KGraphServiceBuilder.build_request(
            request_op=graph_list_op
        )

        response = client.post(request)

        response_dict = json.loads(response)

        results = KGraphServiceParser.parse_kgraphservice_response(response_dict)

        results_dict: dict | None = results.get('results_dict', None)

        if results_dict is not None:

            graph_list: list = results_dict.get('graph_list', [])

            vital_graph_list = []

            for g in graph_list:
                vg = VitalNamespace()
                vg.from_dict(g)
                vital_graph_list.append(vg)

            return vital_graph_list

        return []

    def check_create_kgraph(self, graph_uri: str) -> bool:
        pass

    def create_kgraph(self, graph_uri: str) -> bool:
        pass

    def delete_kgraph(self, graph_uri: str) -> bool:
        pass

    def purge_kgraph(self, graph_uri: str) -> bool:
        pass

    def get_kgraph_all_objects(self, graph_uri: str, limit=100, offset=0) -> ResultList:
        pass

    def insert_object(self, graph_uri: str, graph_object: G) -> VitalServiceStatus:
        pass

    def insert_object_list(self, graph_uri: str, graph_object_list: List[G]) -> VitalServiceStatus:
        pass

    def update_object(self, graph_object: G, graph_uri: str, *, upsert: bool = False) -> VitalServiceStatus:
        pass

    def update_object_list(self, graph_object_list: List[G], graph_uri: str, *,
                           upsert: bool = False) -> VitalServiceStatus:
        pass

    def get_object(self, object_uri: str, graph_uri: str | None = None) -> G:
        pass

    def get_object_list(self, object_uri_list: List[str], graph_uri: str | None = None) -> ResultList:
        pass

    def delete_object(self, object_uri: str, graph_uri: str | None = None) -> VitalServiceStatus:
        pass

    def delete_object_list(self, object_uri_list: List[str], graph_uri: str | None = None) -> VitalServiceStatus:
        pass

    def query(self, graph_uri: str, sparql_query: str) -> ResultList:
        pass

    def query_construct(self, graph_uri: str, sparql_query: str, binding_list: List[Tuple[str, str]]) -> ResultList:
        pass

    def get_interaction_list(self, graph_uri: str, limit=100, offset=0) -> ResultList:
        pass

    def get_interaction_graph(self, graph_uri: str, interaction: KGInteraction, limit=100, offset=0) -> ResultList:
        pass

    def get_interaction_frames(self, graph_uri: str, interaction: KGInteraction, limit=100, offset=0) -> PartList:
        pass

    def get_interaction_nodes(self, graph_uri: str, interaction: KGInteraction, kgnode_type: Type[KGN], limit=100,
                              offset=0) -> ResultList:
        pass

    def get_frame(self, graph_uri: str, frame_uri: str, limit=100, offset=0) -> KGFP:
        pass

    def get_frames(self, graph_uri: str, frame_uri_list: List[str], limit=100, offset=0) -> PartList:
        pass

    def get_frame_id(self, graph_uri: str, frame_id: str, limit=100, offset=0) -> KGFP:
        pass

    def get_frames_id(self, graph_uri: str, frame_id_list: List[str], limit=100, offset=0) -> PartList:
        pass

    def get_frames_root(self, graph_uri: str, root_uri: str, limit=100, offset=0) -> PartList:
        pass

    def get_kgraph_objects_type(self, graph_uri: str, class_uri: str, include_subclasses=True, limit=100,
                               offset=0) -> ResultList:
        pass

    def get_kgraph_objects_tag(self, graph_uri: str, kg_graph_uri: str, limit=100, offset=0) -> ResultList:
        pass

    def delete_frame(self, graph_uri: str, frame_uri: str) -> VitalServiceStatus:
        pass

    def delete_frames(self, graph_uri: str, frame_uri_list: List[str]) -> VitalServiceStatus:
        pass

    def delete_frame_id(self, graph_uri: str, frame_id: str) -> VitalServiceStatus:
        pass

    def delete_frames_id(self, graph_uri: str, frame_id_list: List[str]) -> VitalServiceStatus:
        pass

    def delete_kgraph_objects_tag(self, graph_uri: str, kg_graph_uri: str) -> VitalServiceStatus:
        pass

# use client to connect to rest implementation

    def get_kgraph_info(self, graph_uri: str) -> KGraphInfo:
        pass

    def get_frame_info(self, graph_uri: str) -> FrameInfo:
        pass

    def get_interaction_info(self, graph_uri: str) -> InteractionInfo:
        pass

    def metaql_select_query(self, *,
                            select_query: SelectQuery
                            ) -> MetaQLResult:

        client = KGraphServiceClient(
            host=self._host, port=self._port
        )

        query_op = KGraphServiceBuilder.build_query_op(
            metaql_query=select_query
        )

        request = KGraphServiceBuilder.build_request(
            request_op=query_op
        )

        # print(request)

        response = client.post(request)

        response_dict = json.loads(response)

        results = KGraphServiceParser.parse_kgraphservice_response(response_dict)

        results_dict: dict | None = results.get('results_dict', None)

        if results_dict is not None:

            offset = results_dict.get('offset', None)
            limit = results_dict.get('limit', None)
            result_count = results_dict.get('result_count', None)
            total_result_count = results_dict.get('total_result_count', 0)
            binding_list = results_dict.get('binding_list', [])
            metaql_result_list = results_dict.get('result_list', [])
            metaql_result_object_list = results_dict.get('result_object_list', [])

            go_result_object_list = []

            for obj in metaql_result_object_list:
                go = GraphObject.from_json_map(obj)
                go_result_object_list.append(go)

            result_list = []

            for metaql_re in metaql_result_list:

                graph_object_dict = metaql_re.get('graph_object', None)

                graph_object = GraphObject.from_json_map(graph_object_dict)

                score = metaql_re.get('score', 1.0)

                if graph_object is not None:
                    re = ResultElement(
                        graph_object=graph_object,
                        score=score
                    )
                    result_list.append(re)

            metaql_results = MetaQLResult(
                offset=offset,
                limit=limit,
                total_result_count=total_result_count,
                binding_list=binding_list,
                result_object_list=go_result_object_list,
                result_list=result_list
            )

            return metaql_results

        metaql_results = MetaQLResult()

        return metaql_results

    def metaql_graph_query(self, *,
                           graph_query: GraphQuery
                           ) -> MetaQLResult:

        client = KGraphServiceClient(
            host=self._host, port=self._port
        )

        query_op = KGraphServiceBuilder.build_query_op(
            metaql_query=graph_query
        )

        request = KGraphServiceBuilder.build_request(
            request_op=query_op
        )

        response = client.post(request)

        response_dict = json.loads(response)

        results = KGraphServiceParser.parse_kgraphservice_response(response_dict)

        results_dict: dict | None = results.get('results_dict', None)

        if results_dict is not None:

            offset = results_dict.get('offset', None)
            limit = results_dict.get('limit', None)
            result_count = results_dict.get('result_count', None)
            total_result_count = results_dict.get('total_result_count', 0)
            binding_list = results_dict.get('binding_list', [])
            metaql_result_list = results_dict.get('result_list', [])
            metaql_result_object_list = results_dict.get('result_object_list', [])

            go_result_object_list = []

            for obj in metaql_result_object_list:
                go = GraphObject.from_json_map(obj)
                go_result_object_list.append(go)

            result_list = []

            for metaql_re in metaql_result_list:

                graph_object_dict = metaql_re.get('graph_object', None)

                graph_object = GraphObject.from_json_map(graph_object_dict)

                score = metaql_re.get('score', 1.0)
                if graph_object is not None:
                    re = ResultElement(
                        graph_object=graph_object,
                        score=score
                    )
                    result_list.append(re)

            metaql_results = MetaQLResult(
                offset=offset,
                limit=limit,
                total_result_count=total_result_count,
                binding_list=binding_list,
                result_object_list=go_result_object_list,
                result_list=result_list
            )

            return metaql_results

        metaql_results = MetaQLResult()

        return metaql_results
