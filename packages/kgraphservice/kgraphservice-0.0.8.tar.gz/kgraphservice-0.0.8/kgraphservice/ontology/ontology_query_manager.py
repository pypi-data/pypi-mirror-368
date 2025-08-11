from typing import List
from vital_ai_domain.model.VitalOntNode import VitalOntNode
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from vital_ai_vitalsigns.vitalsigns import VitalSigns


class OntologyQueryManager:

    def __int__(self):
        pass

    def get_ontology_iri_list(self) -> List[str]:
        iri_list = []
        vs = VitalSigns()

        ont_manager = vs.get_ontology_manager()

        return ont_manager.get_ontology_iri_list()

    # TODO wrap functions from vs ont manager to return graph objects

    def get_ont_node(self, ontology_iri, node_class_uri):
        vs = VitalSigns()
        # get node info from vs ont manager
        # URI is a function of the class uri?
        # URI = urn:VitalOntNode + (class uri - schema)
        node = VitalOntNode()
        # set uri, name, class uri, etc.
        return node

    def search_domain_ontology(self, search_string) -> List[GraphObject]:

        vs = VitalSigns()

        ont_manager = vs.get_ontology_manager()

        graph = ont_manager.get_domain_graph()

        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?class
        WHERE {{
            ?class a owl:Class .
            FILTER regex(str(?class), "{search_string}", "i")
        }}
        """

        results = graph.query(query)

        graph_results = []

        for row in results:
            class_uri = row['class']

            ont_node = VitalOntNode()
            ont_node.URI = URIGenerator.generate_uri()
            ont_node.name = class_uri
            graph_results.append(ont_node)

        return graph_results

