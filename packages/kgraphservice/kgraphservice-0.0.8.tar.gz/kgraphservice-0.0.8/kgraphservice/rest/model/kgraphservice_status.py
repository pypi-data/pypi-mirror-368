from typing import Literal, Optional

from typing_extensions import TypedDict


OK_KGRAPHSERVICE_STATUS_TYPE = "OK_KGRAPHSERVICE_STATUS_TYPE"

KGRAPHSERVICE_STATUS_TYPE = Literal[
    "OK_KGRAPHSERVICE_STATUS_TYPE"
]


class KGraphServiceStatus(TypedDict):

    kgraphservice_class: str

    status_type: KGRAPHSERVICE_STATUS_TYPE

    status_code: Optional[int]

    status_message: Optional[str]

