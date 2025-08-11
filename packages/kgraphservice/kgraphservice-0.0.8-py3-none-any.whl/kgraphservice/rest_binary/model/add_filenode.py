from typing import TypedDict
from vital_ai_domain.model.FileNode import FileNode


class AddFileNode(TypedDict):

    kgraphservice_binary_class: str
    account_uri: str
    file_node: FileNode

