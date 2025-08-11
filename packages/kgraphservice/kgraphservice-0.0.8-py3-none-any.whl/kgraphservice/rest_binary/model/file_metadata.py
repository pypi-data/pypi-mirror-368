from typing import Optional, List

from typing_extensions import TypedDict


class FileMetadata(TypedDict):
    description: Optional[str]
    tags: Optional[List[str]]
    author: Optional[str]

