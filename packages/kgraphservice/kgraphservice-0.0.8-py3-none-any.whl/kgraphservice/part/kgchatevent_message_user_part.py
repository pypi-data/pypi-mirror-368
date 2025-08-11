from typing import List, Optional, TypeVar
from ai_haley_kg_domain.model.KGFrame import KGFrame
from ai_haley_kg_domain.model.KGSlot import KGSlot
from vital_ai_vitalsigns.collection.graph_collection import GraphCollection
from vital_ai_vitalsigns.model.GraphObject import GraphObject

from kgraphservice.part.kgchatevent_message_part import KGChatEventMessagePart
from kgraphservice.part.kgnode_part import KGNodePart

G = TypeVar('G', bound=Optional[GraphObject])


class KGChatEventUserMessagePart(KGChatEventMessagePart):
    pass
