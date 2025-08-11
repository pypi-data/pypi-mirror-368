from enum import Enum

from vital_ai_domain.model.FileNode import FileNode


class BinaryStatusType(Enum):
    OK = "OK"
    ERROR = "ERROR"
    FAIL = "FAIL"


class KGraphServiceBinaryStatus:

    def __init__(self, *,
                 status: BinaryStatusType = BinaryStatusType.OK,
                 status_code: int = 0,
                 status_message: str = "",
                 file_node: FileNode = None,
                 file_node_metadata: dict = None):
        self.status = status
        self.status_code = status_code
        self.status_message = status_message

        self.file_node = file_node
        self.file_node_metadata = file_node_metadata



