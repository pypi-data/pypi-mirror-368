from typing import TypeVar, Optional, List
from vital_ai_vitalsigns.collection.graph_collection import GraphCollection
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from kgraphservice.part.kgnode_part import KGNodePart

G = TypeVar('G', bound=Optional[GraphObject])


class KGDocumentPart(KGNodePart):
    def __init__(self, *, data: List[G] = [], score: float = 1.0,
                 base: G = None,
                 in_edge: G = None,
                 graph_collection: GraphCollection | None = None):

        super().__init__(data=data, score=score,
                         base=base,
                         in_edge=in_edge,
                         graph_collection=graph_collection)

