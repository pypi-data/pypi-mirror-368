from abc import ABC
from typing import AsyncIterator, Optional, BinaryIO, List, Dict


class BinaryService(ABC):

    async def upload_stream(self, byte_stream: AsyncIterator[bytes], bucket_name: str, key_name: str):
        pass

    def upload_file_sync(self, file_data: bytes, bucket_name: str, key_name: str):
        pass

    def get_file_sync(self, bucket_name: str, key_name: str) -> bytes:
        pass

    async def get_file_async(self, bucket_name: str, key_name: str, output_stream: BinaryIO):
        pass

    def list_files(self, bucket_name: str, prefix: Optional[str] = None, page_number: int = 1, page_size: int = 100) -> List[str]:
        pass

    def delete_file(self, bucket_name: str, key_name: str):
       pass

    def get_file_metadata(self, bucket_name: str, key_name: str) -> Dict[str, str]:
        pass

