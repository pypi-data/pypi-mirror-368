from io import BytesIO
from typing import Optional, Dict, Any, AsyncIterator

from fastapi import UploadFile
from vital_ai_domain.model.FileNode import FileNode
from vital_ai_vitalsigns.service.vital_service import VitalService
from kgraphservice.binary.binary_service import BinaryService
from kgraphservice.binary.s3_impl import S3Impl
from kgraphservice.rest_binary.impl.kgraphservice_binary_status import KGraphServiceBinaryStatus


async def file_to_async_iterator(file: UploadFile, chunk_size: int = 8192) -> AsyncIterator[bytes]:
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        yield chunk


class KGraphServiceRESTBinaryImpl:
    def __init__(self, *, vitalservice: VitalService = None, org_id: str = "", app_id: str = "", impl: BinaryService):
        self._vitalservice = vitalservice
        self._impl = impl
        self._org_id = org_id
        self._app_id = app_id

    # add file node and data
    async def add_filenode(self, *,
                           bucket_name: str,
                           account_uri: str,
                           filenode: FileNode,
                           file: UploadFile) -> KGraphServiceBinaryStatus:

        file_name = str(filenode.fileName)

        # potentially add login URI into the key as per some haley saas cases

        # would want to keep naming pattern in sync with haley saas pattern
        # so can share paths

        # the groovy version puts files in account path and
        # uses pattern for filename like:
        # "cherry_blossoms_1-1713994648001-662.png
        # path + '-' + System.currentTimeMillis() + '-' + new Random().nextInt(10000)
        # so it's filename + current time + random + file extension

        key_name = f"{self._org_id}/{self._app_id}/{account_uri}/{file_name}"

        min_chunk_size = 5 * 1024 * 1024
        buffer = await file.read(min_chunk_size)

        if len(buffer) < min_chunk_size:
            self.upload_file_sync(buffer, bucket_name, key_name)
        else:
            async def file_byte_stream():
                yield buffer  # Yield the initial 5 MB chunk
                while chunk := await file.read(min_chunk_size):
                    yield chunk

            await self.upload_file_async(file_byte_stream(), bucket_name, key_name)

        # success = True
        # print(f"Upload status: Success: {success}")

        print(f"After Upload: {key_name}")

        status = KGraphServiceBinaryStatus()
        return status

    # delete file node and data
    async def delete_filenode(self, *, account_uri: str, filenode_uri: str) -> KGraphServiceBinaryStatus:
        bucket_name = f"{self._org_id}/{self._app_id}/{account_uri}"

        status = KGraphServiceBinaryStatus()
        return status

    # get file node and data
    async def get_filenode(self, *, account_uri: str, filenode_uri: str) -> KGraphServiceBinaryStatus:
        bucket_name = f"{self._org_id}/{self._app_id}/{account_uri}"

        file_node = None

        status = KGraphServiceBinaryStatus(
            file_node=file_node
        )

        return status

    # update file node and data
    async def update_filenode(self, *, account_uri: str, filenode: FileNode, data:  AsyncIterator[bytes]) -> KGraphServiceBinaryStatus:
        bucket_name = f"{self._org_id}/{self._app_id}/{account_uri}"
        status = KGraphServiceBinaryStatus()
        return status

    # get file node metadata
    async def get_filenode_metadata(self, *, account_uri: str, filenode_uri: str) -> KGraphServiceBinaryStatus:
        bucket_name = f"{self._org_id}/{self._app_id}/{account_uri}"

        file_node_metadata = {}

        status = KGraphServiceBinaryStatus(
            file_node_metadata=file_node_metadata
        )
        return status

    async def upload_file_async(self, file_byte_stream, bucket_name: str, key_name: str):
        await self._impl.upload_stream(file_byte_stream, bucket_name=bucket_name, key_name=key_name)

    async def download_file_async(self, bucket_name: str, key_name: str) -> BytesIO:
        output_stream = BytesIO()
        await self._impl.get_file_async(
            bucket_name=bucket_name,
            key_name=key_name,
            output_stream=output_stream)

        output_stream.seek(0)
        return output_stream

    def upload_file_sync(self, file_data: bytes, bucket_name: str, key_name: str, metadata: Optional[Dict[str, Any]] = None):
        self._impl.upload_file_sync(file_data, bucket_name=bucket_name, key_name=key_name)

    def download_file_sync(self, bucket_name: str, key_name: str) -> bytes:
        return self._impl.get_file_sync(bucket_name=bucket_name, key_name=key_name)

    def list_files(self, bucket_name: str, prefix: Optional[str] = None) -> list[str]:
        return self._impl.list_files(bucket_name=bucket_name, prefix=prefix)

    def delete_file(self, bucket_name: str, key_name: str):
        self._impl.delete_file(bucket_name=bucket_name, key_name=key_name)

    def get_file_metadata(self, bucket_name: str, key_name: str) -> Dict[str, Any]:
        return self._impl.get_file_metadata(bucket_name=bucket_name, key_name=key_name)
