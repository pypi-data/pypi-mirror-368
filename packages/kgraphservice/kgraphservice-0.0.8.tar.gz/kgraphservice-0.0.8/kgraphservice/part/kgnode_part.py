from typing import TypeVar, Optional, List
from vital_ai_vitalsigns.collection.graph_collection import GraphCollection
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.part.graph_part import GraphPart

G = TypeVar('G', bound=Optional[GraphObject])


class KGNodePart(GraphPart):

    def __init__(self, *, data: List[G] = [], score: float = 1.0,
                 base: G = None,
                 in_edge: G = None,
                 graph_collection: GraphCollection | None = None):
        super().__init__(data, score, graph_collection=graph_collection)

        if data:
            self._init = True
        else:
            self._init = False

        self._modified = False

        # the underlying mutable sequence is already storing the
        # list, so don't need to store in _data
        # but need to make it consistent
        self._data = data
        self._base = base
        self._in_edge = in_edge
        rest_list = []
        for g in data:
            if not (g == base or g == in_edge):
                rest_list.append(g)
        self._rest = rest_list

    def set_data(self, data: List[G], score: float = 1.0, *,
                 base: G = None,
                 in_edge: G = None):

        # TODO update the underlying mutable sequence in GraphPart

        if data:
            self._init = True
        else:
            self._init = False

        self._modified = False

        self._data = data
        self._base = base
        self._in_edge = in_edge
        rest_list = []
        for g in data:
            if not (g == base or g == in_edge):
                rest_list.append(g)
        self._rest = rest_list

    def get_data(self) -> List[G]:
        return self._data

    def get_base(self) -> G:
        return self._base

    def get_in_edge(self) -> G:
        return self._in_edge

    def get_rest(self) -> List[G]:
        return self._rest

    def set_modified(self):
        self._modified = True

    def reset_modified(self):
        self._modified = False

    def is_modified(self):
        return self._modified

    def is_init(self):
        return self._init


