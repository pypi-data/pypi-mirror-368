from typing import Optional
from typing_extensions import TypedDict


class ListFilesRequest(TypedDict):
    prefix: Optional[str]
