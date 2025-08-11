from typing import List
from vital_ai_vitalsigns.ontology.ontology import Ontology
from vital_ai_vitalsigns.service.graph.binding import Binding
from kgraphservice.query.kgslot_criterion import KGSlotCriterion
from kgraphservice.query.construct_query import ConstructQuery


class FrameQueryGenerator:

    @classmethod
    def generate_uri_query(cls, frame_uri: str) -> ConstructQuery:

        namespace_list = cls.get_default_namespace_list()

        binding_list = [
            Binding("?frame", "urn:hasFrame"),
            Binding("?slotEdge", "urn:hasSlotEdge"),
            Binding("?slot", "urn:hasSlot")
        ]

        slot_class_list = cls.get_slot_class_list()

        frame_query = f"""
            {{
                VALUES ?frameURI {{
                    <{frame_uri}>
                }}
                
                VALUES ?slotDataType {{
                    {slot_class_list}
                }}

                BIND(?frameURI AS ?frame)

                ?frame rdf:type haley-ai-kg:KGFrame .

                ?slotEdge vital-core:hasEdgeSource ?frame .
                ?slotEdge vital-core:hasEdgeDestination ?slot .
                ?slotEdge rdf:type haley-ai-kg:Edge_hasKGSlot .

                ?slot rdf:type ?slotType .
            }}

            FILTER(?slotType IN (?slotDataType))
        """

        construct_query = ConstructQuery(namespace_list, binding_list, frame_query)

        return construct_query

    @classmethod
    def generate_uri_list_query(cls, frame_uri_list: List[str]) -> ConstructQuery:

        frame_uri_values = "\n".join([f"<{uri}>" for uri in frame_uri_list])

        namespace_list = cls.get_default_namespace_list()

        binding_list = [
            Binding("?frame", "urn:hasFrame"),
            Binding("?slotEdge", "urn:hasSlotEdge"),
            Binding("?slot", "urn:hasSlot")
        ]

        slot_class_list = cls.get_slot_class_list()

        frame_query = f"""
            {{
                VALUES ?frameURI {{
                    {frame_uri_values}
                }}

                VALUES ?slotDataType {{
                    {slot_class_list}
                }}

                BIND(?frameURI AS ?frame)

                ?frame rdf:type haley-ai-kg:KGFrame .

                ?slotEdge vital-core:hasEdgeSource ?frame .
                ?slotEdge vital-core:hasEdgeDestination ?slot .
                ?slotEdge rdf:type haley-ai-kg:Edge_hasKGSlot .

                ?slot rdf:type ?slotType .
            }}

            FILTER(?slotType IN (?slotDataType))
            """

        construct_query = ConstructQuery(namespace_list, binding_list, frame_query)

        return construct_query

    @classmethod
    def generate_id_query(cls, frame_id: str) -> ConstructQuery:

        namespace_list = cls.get_default_namespace_list()

        binding_list = [
            Binding("?frame", "urn:hasFrame"),
            Binding("?slotEdge", "urn:hasSlotEdge"),
            Binding("?slot", "urn:hasSlot")
        ]

        root_binding = "?frame"

        slot_class_list = cls.get_slot_class_list()

        frame_query = f"""
                    {{
                        VALUES ?kg_identifier {{
                            "{frame_id}"^^<http://www.w3.org/2001/XMLSchema#string>
                        }}

                        VALUES ?slotDataType {{
                            {slot_class_list}
                        }}

                        BIND(?kg_identifier AS ?frame_id)

                        ?frame rdf:type haley-ai-kg:KGFrame .
                        ?frame haley-ai-kg:hasKGIdentifier ?frame_id .

                        ?slotEdge vital-core:hasEdgeSource ?frame .
                        ?slotEdge vital-core:hasEdgeDestination ?slot .
                        ?slotEdge rdf:type haley-ai-kg:Edge_hasKGSlot .

                        ?slot rdf:type ?slotType .
                    }}

                    FILTER(?slotType IN (?slotDataType))
                """

        construct_query = ConstructQuery(namespace_list, binding_list, frame_query, root_binding)

        return construct_query

    @classmethod
    def generate_id_list_query(cls, frame_id_list: List[str]) -> ConstructQuery:

        frame_id_values = "\n".join(
            [f'"{frame_id}"^^<http://www.w3.org/2001/XMLSchema#string>' for frame_id in frame_id_list])

        namespace_list = cls.get_default_namespace_list()

        binding_list = [
            Binding("?frame", "urn:hasFrame"),
            Binding("?slotEdge", "urn:hasSlotEdge"),
            Binding("?slot", "urn:hasSlot")
        ]

        slot_class_list = cls.get_slot_class_list()

        frame_query = f"""
                        {{
                            VALUES ?kg_identifier {{
                                {frame_id_values}
                        }}

                        VALUES ?slotDataType {{
                            {slot_class_list}
                        }}

                        BIND(?kg_identifier AS ?frame_id)

                        ?frame rdf:type haley-ai-kg:KGFrame .
                        ?frame haley-ai-kg:hasKGIdentifier ?frame_id .

                        ?slotEdge vital-core:hasEdgeSource ?frame .
                        ?slotEdge vital-core:hasEdgeDestination ?slot .
                        ?slotEdge rdf:type haley-ai-kg:Edge_hasKGSlot .

                        ?slot rdf:type ?slotType .
                    }}

                    FILTER(?slotType IN (?slotDataType))
                    """

        construct_query = ConstructQuery(namespace_list, binding_list, frame_query)

        return construct_query

    @classmethod
    def generate_criteria_query(cls,
                                criteria_list: List[KGSlotCriterion],
                                limit: int = 100, offset: int = 0) -> ConstructQuery:

        namespace_list = []
        binding_list = []
        query = ""

        construct_query = ConstructQuery(namespace_list, binding_list, query, limit, offset)

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

    @classmethod
    def get_slot_class_list(cls):

        slot_class_list = """
            haley-ai-kg:KGSlot
            haley-ai-kg:KGAudioSlot
            haley-ai-kg:KGBooleanSlot
            haley-ai-kg:KGChoiceOptionSlot
            haley-ai-kg:KGChoiceSlot
            haley-ai-kg:KGCodeSlot
            haley-ai-kg:KGCurrencySlot
            haley-ai-kg:KGDateTimeSlot
            haley-ai-kg:KGDoubleSlot
            haley-ai-kg:KGEntitySlot
            haley-ai-kg:KGFileUploadSlot
            haley-ai-kg:KGGeoLocationSlot
            haley-ai-kg:KGImageSlot
            haley-ai-kg:KGIntegerSlot
            haley-ai-kg:KGJSONSlot
            haley-ai-kg:KGLongSlot
            haley-ai-kg:KGLongTextSlot
            haley-ai-kg:KGMultiChoiceOptionSlot
            haley-ai-kg:KGMultiChoiceSlot
            haley-ai-kg:KGMultiTaxonomyOptionSlot
            haley-ai-kg:KGMultiTaxonomySlot
            haley-ai-kg:KGPropertySlot
            haley-ai-kg:KGRunSlot
            haley-ai-kg:KGTaxonomyOptionSlot
            haley-ai-kg:KGTaxonomySlot
            haley-ai-kg:KGTextSlot
            haley-ai-kg:KGURISlot
            haley-ai-kg:KGVideoSlot
        """

        return slot_class_list

