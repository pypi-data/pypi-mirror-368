from typing import TypedDict, Literal, Optional
from vital_ai_domain.model.FileNode import FileNode
from kgraphservice.rest_binary.model.status_response import StatusType


class FileNodeResponse(TypedDict):

    kgraphservice_binary_class: str

    status: StatusType
    status_code: Optional[int]
    status_message: Optional[str]

    file_node: Optional[FileNode]
    file_node_metadata: Optional[dict]




