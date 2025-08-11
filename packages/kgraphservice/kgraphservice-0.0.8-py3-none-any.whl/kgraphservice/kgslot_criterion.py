from kgraphservice.query.kg_comparator import KGComparator


class KGSlotCriterion:

    def __init__(self, slot_type_uri: str, comparator: KGComparator, value):
        self.slot_type_uri = slot_type_uri
        self.comparator = comparator
        self.value = value


