from abc import ABC, abstractmethod
from typing import List, TypeVar, Optional, Type, Tuple
from ai_haley_kg_domain.model.KGInteraction import KGInteraction
from ai_haley_kg_domain.model.KGNode import KGNode
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.query.part_list import PartList
from vital_ai_vitalsigns.query.result_list import ResultList
from vital_ai_vitalsigns.service.vital_namespace import VitalNamespace
from vital_ai_vitalsigns.service.vital_service_status import VitalServiceStatus
from kgraphservice.ontology.ontology_query_manager import OntologyQueryManager
from kgraphservice.part.kgframe_part import KGFramePart

G = TypeVar('G', bound=Optional[GraphObject])
KGN = TypeVar('KGN', bound=Optional[KGNode])
KGFP = TypeVar('KGFP', bound=Optional[KGFramePart])


class KGraphServiceInterface(ABC):
    @abstractmethod
    def get_ontology_query_manager(self) -> OntologyQueryManager:
        pass

    @abstractmethod
    def get_graph(self, graph_uri: str) -> VitalNamespace:
        pass

    @abstractmethod
    def list_graphs(self) -> List[VitalNamespace]:
        pass

    @abstractmethod
    def check_create_graph(self, graph_uri: str) -> bool:
        pass

    @abstractmethod
    def create_graph(self, graph_uri: str) -> bool:
        pass

    @abstractmethod
    def delete_graph(self, graph_uri: str) -> bool:
        pass

    @abstractmethod
    def purge_graph(self, graph_uri: str) -> bool:
        pass

    @abstractmethod
    def get_graph_all_objects(self, graph_uri: str, limit=100, offset=0) -> ResultList:
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
    def filter_query(self, graph_uri: str, sparql_query: str) -> ResultList:
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
    def get_graph_objects_type(self, graph_uri: str, class_uri: str, include_subclasses=True, limit=100,
                               offset=0) -> ResultList:
        pass

    @abstractmethod
    def get_graph_objects_tag(self, graph_uri: str, kg_graph_uri: str, limit=100, offset=0) -> ResultList:
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
    def delete_graph_objects_tag(self, graph_uri: str, kg_graph_uri: str) -> VitalServiceStatus:
        pass
