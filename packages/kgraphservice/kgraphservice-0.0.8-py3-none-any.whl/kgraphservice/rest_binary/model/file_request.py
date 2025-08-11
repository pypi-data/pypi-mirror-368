from typing import Optional

from typing_extensions import TypedDict


class FileRequest(TypedDict):
    prefix: Optional[str]
    key_name: str
