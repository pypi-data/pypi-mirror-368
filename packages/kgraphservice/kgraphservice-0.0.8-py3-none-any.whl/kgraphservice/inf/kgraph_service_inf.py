from abc import ABC, abstractmethod
from typing import List, TypeVar, Optional, Type, Tuple
from ai_haley_kg_domain.model.KGInteraction import KGInteraction
from ai_haley_kg_domain.model.KGNode import KGNode
from vital_ai_vitalsigns.metaql.metaql_query import GraphQuery, SelectQuery
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.query.metaql_result import MetaQLResult
from vital_ai_vitalsigns.query.part_list import PartList
from vital_ai_vitalsigns.query.result_list import ResultList
from vital_ai_vitalsigns.service.vital_namespace import VitalNamespace
from vital_ai_vitalsigns.service.vital_service_status import VitalServiceStatus
from kgraphservice.info.frame_info import FrameInfo
from kgraphservice.info.interaction_info import InteractionInfo
from kgraphservice.info.kgraph_info import KGraphInfo
from kgraphservice.part.kgframe_part import KGFramePart

G = TypeVar('G', bound=Optional[GraphObject])
KGN = TypeVar('KGN', bound=Optional[KGNode])
KGFP = TypeVar('KGFP', bound=Optional[KGFramePart])

# TODO
# remove non metaql query functions
# add KGTask functions for managing kg tasks
# add create task, update task, get task, remove task
# add run task, stop task, schedule task, cancel task
# add assign task (set execution engine type)
# note: update task would be limited based on status of task
# remove task would be limited based on status of task

class KGraphServiceInterface(ABC):

    @abstractmethod
    def get_kgraph(self, graph_uri: str) -> VitalNamespace:
        pass

    @abstractmethod
    def list_kgraphs(self) -> List[VitalNamespace]:
        pass

    @abstractmethod
    def check_create_kgraph(self, graph_uri: str) -> bool:
        pass

    @abstractmethod
    def create_kgraph(self, graph_uri: str) -> bool:
        pass

    @abstractmethod
    def delete_kgraph(self, graph_uri: str) -> bool:
        pass

    @abstractmethod
    def purge_kgraph(self, graph_uri: str) -> bool:
        pass

    @abstractmethod
    def get_kgraph_all_objects(self, graph_uri: str, limit=100, offset=0) -> ResultList:
        pass

    @abstractmethod
    def insert_object(self, graph_uri: str, graph_object: G) -> VitalServiceStatus:
        pass

    @abstractmethod
    def insert_object_list(self, graph_uri: str, graph_object_list: List[G]) -> VitalServiceStatus:
        pass

    @abstractmethod
    def update_object(self, graph_object: G, graph_uri: str, *, upsert: bool = False) -> VitalServiceStatus:
        pass

    @abstractmethod
    def update_object_list(self, graph_object_list: List[G], graph_uri: str, *, upsert: bool = False) -> VitalServiceStatus:
        pass

    @abstractmethod
    def get_object(self, object_uri: str, graph_uri: str | None = None) -> G:
        pass

    @abstractmethod
    def get_object_list(self, object_uri_list: List[str], graph_uri: str | None = None) -> ResultList:
        pass

    @abstractmethod
    def delete_object(self, object_uri: str, graph_uri: str | None = None) -> VitalServiceStatus:
        pass

    @abstractmethod
    def delete_object_list(self, object_uri_list: List[str], graph_uri: str | None = None) -> VitalServiceStatus:
        pass

    @abstractmethod
    def query(self, graph_uri: str, sparql_query: str) -> ResultList:
        pass

        # Tuple[binding name, property uri]

    @abstractmethod
    def query_construct(self, graph_uri: str, sparql_query: str, binding_list: List[Tuple[str, str]]) -> ResultList:
        pass

    @abstractmethod
    def get_interaction_list(self, graph_uri: str, limit=100, offset=0) -> ResultList:
        pass

    @abstractmethod
    def get_interaction_graph(self, graph_uri: str, interaction: KGInteraction, limit=100, offset=0) -> ResultList:
        pass

    @abstractmethod
    def get_interaction_frames(self, graph_uri: str, interaction: KGInteraction, limit=100, offset=0) -> PartList:
        pass

    @abstractmethod
    def get_interaction_nodes(self, graph_uri: str, interaction: KGInteraction, kgnode_type: Type[KGN], limit=100,
                              offset=0) -> ResultList:
        pass

    @abstractmethod
    def get_frame(self, graph_uri: str, frame_uri: str, limit=100, offset=0) -> KGFP:
        pass

    @abstractmethod
    def get_frames(self, graph_uri: str, frame_uri_list: List[str], limit=100, offset=0) -> PartList:
        pass

    @abstractmethod
    def get_frame_id(self, graph_uri: str, frame_id: str, limit=100, offset=0) -> KGFP:
        pass

    @abstractmethod
    def get_frames_id(self, graph_uri: str, frame_id_list: List[str], limit=100, offset=0) -> PartList:
        pass

    @abstractmethod
    def get_frames_root(self, graph_uri: str, root_uri: str, limit=100, offset=0) -> PartList:
        pass

    @abstractmethod
    def get_kgraph_objects_type(self, graph_uri: str, class_uri: str, include_subclasses=True, limit=100,
                               offset=0) -> ResultList:
        pass

    @abstractmethod
    def get_kgraph_objects_tag(self, graph_uri: str, kg_graph_uri: str, limit=100, offset=0) -> ResultList:
        pass

    @abstractmethod
    def delete_frame(self, graph_uri: str, frame_uri: str) -> VitalServiceStatus:
        pass

    @abstractmethod
    def delete_frames(self, graph_uri: str, frame_uri_list: List[str]) -> VitalServiceStatus:
        pass

    @abstractmethod
    def delete_frame_id(self, graph_uri: str, frame_id: str) -> VitalServiceStatus:
        pass

    @abstractmethod
    def delete_frames_id(self, graph_uri: str, frame_id_list: List[str]) -> VitalServiceStatus:
        pass

    @abstractmethod
    def delete_kgraph_objects_tag(self, graph_uri: str, kg_graph_uri: str) -> VitalServiceStatus:
        pass

    @abstractmethod
    def get_kgraph_info(self, graph_uri: str) -> KGraphInfo:
        pass

    @abstractmethod
    def get_frame_info(self, graph_uri: str) -> FrameInfo:
        pass

    @abstractmethod
    def get_interaction_info(self, graph_uri: str) -> InteractionInfo:
        pass

    @abstractmethod
    def metaql_select_query(self, *,
                            select_query: SelectQuery
                            ) -> MetaQLResult:
        pass

    @abstractmethod
    def metaql_graph_query(self, *,
                           graph_query: GraphQuery
                           ) -> MetaQLResult:
        pass

