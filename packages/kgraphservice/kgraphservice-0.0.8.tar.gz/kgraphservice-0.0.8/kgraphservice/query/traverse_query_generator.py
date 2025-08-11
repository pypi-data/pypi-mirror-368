from enum import Enum
from typing import Optional

from vital_ai_vitalsigns.ontology.ontology import Ontology
from vital_ai_vitalsigns.service.graph.binding import Binding
from kgraphservice.query.construct_query import ConstructQuery


class QueryDirection(Enum):
    OUTGOING = 'outgoing'
    INCOMING = 'incoming'
    BOTH = 'both'


class TraverseQueryGenerator:

    @classmethod
    def generate_traverse_query(cls, source_uri: str, *,
                                query_direction: QueryDirection = QueryDirection.OUTGOING,
                                edge_class_uri: Optional[str] = None,
                                include_edge_subclasses: bool = False,
                                target_class_uri: Optional[str] = None,
                                include_target_subclasses: bool = False
                                ):

        namespace_list = cls.get_default_namespace_list()

        binding_list = [
            Binding("?uri", "urn:hasSourceUri"),
            Binding("?edge", "urn:hasEdgeUri"),
            Binding("?direction", "urn:hasDirectionUri"),
            Binding("?target", "urn:hasTargetUri")
        ]

        if target_class_uri:
            target_criterion = f"?target a <{target_class_uri}> ."
        else:
            target_criterion = ""

        if edge_class_uri:
            edge_criterion = f"?edge a <{edge_class_uri}> ."
        else:
            edge_criterion = ""

        if query_direction == QueryDirection.OUTGOING:
            traverse_query = f"""
                    BIND('{source_uri}' AS ?uri)

                    {{
                        ?edge vital-core:hasEdgeSource ?uri ;
                              vital-core:hasEdgeDestination ?target .

                        {edge_criterion}

                        {target_criterion}

                        BIND('urn:outgoing' AS ?direction)
                    }}
                    """

        elif query_direction == QueryDirection.INCOMING:
            traverse_query = f"""
                    BIND('{source_uri}' AS ?uri)

                    {{
                        ?edge vital-core:hasEdgeSource ?target ;
                              vital-core:hasEdgeDestination ?uri .

                        {edge_criterion}

                        {target_criterion}

                        BIND('urn:incoming' AS ?direction)
                    }}
                    """

        elif query_direction == QueryDirection.BOTH:
            traverse_query = f"""
                    BIND('{source_uri}' AS ?uri)

                    {{
                        ?edge vital-core:hasEdgeSource ?uri ;
                              vital-core:hasEdgeDestination ?target .

                        {edge_criterion}

                        {target_criterion}
                        
                        BIND('urn:outgoing' AS ?direction)
                    }}
                    UNION
                    {{
                        ?edge vital-core:hasEdgeSource ?target ;
                              vital-core:hasEdgeDestination ?uri .

                        {edge_criterion}

                        {target_criterion}

                        BIND('urn:incoming' AS ?direction)
                    }}
                    """
        else:
            raise ValueError(
                "Invalid query direction. Use QueryDirection.OUTGOING, QueryDirection.INCOMING, or QueryDirection.BOTH.")

        construct_query = ConstructQuery(namespace_list, binding_list, traverse_query)

        return construct_query

    @classmethod
    def get_default_namespace_list(cls):
        namespace_list = [
            Ontology("vital-core", "http://vital.ai/ontology/vital-core#"),
            Ontology("vital", "http://vital.ai/ontology/vital#"),
            Ontology("vital-aimp", "http://vital.ai/ontology/vital-aimp#"),
            Ontology("haley", "http://vital.ai/ontology/haley"),
            Ontology("haley-ai-question", "http://vital.ai/ontology/haley-ai-question#"),
            Ontology("haley-ai-kg", "http://vital.ai/ontology/haley-ai-kg#")
        ]

        return namespace_list
