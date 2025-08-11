from typing import TypedDict, Optional, Literal

StatusType_OK = "StatusType_OK"
StatusType_ERROR = "StatusType_ERROR"
StatusType_FAIL = "StatusType_FAIL"

StatusType = Literal[
    "StatusType_OK",
    "StatusType_ERROR",
    "StatusType_FAIL"
]


class StatusResponse(TypedDict):

    kgraphservice_binary_class: str
    status: StatusType
    status_code: Optional[int]
    status_message: Optional[str]
