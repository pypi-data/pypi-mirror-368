from typing_extensions import TypedDict


class KGraphServiceModification(TypedDict):

    kgraphservice_class: str

    operation_success: bool

    operation_message: str

    inserted_count: int
    updated_count: int
    deleted_count: int

    indexed_count: int



