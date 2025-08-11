from enum import Enum


class KGComparator(Enum):

    # replace values with URIs from ontology

    EXISTS = "exists"
    NOT_EXISTS = "not_exists"

    EQUALS = "equals"
    NOT_EQUAL_TO = "not_equal_to"

    LESS_THAN = "less_than"
    LESS_EQUAL = "less_equals"

    GREATER_THAN = "greater_than"
    GREATER_EQUAL = "greater_equal"

    # set membership
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"



