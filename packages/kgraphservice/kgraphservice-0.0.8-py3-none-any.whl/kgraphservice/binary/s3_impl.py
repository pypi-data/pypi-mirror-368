import aioboto3
import boto3
import asyncio
from io import BytesIO
from typing import AsyncIterator, Optional, List, Dict, BinaryIO
from boto3.s3.transfer import TransferConfig
from kgraphservice.binary.binary_service import BinaryService


class S3Impl(BinaryService):
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: Optional[str] = None):
        """
        Initialize S3Impl with AWS credentials and region.

        Parameters:
            aws_access_key_id (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
            region_name (str, optional): AWS region name. Default is None.
        """
        self.session = aioboto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.sync_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    async def upload_stream(self, byte_stream: AsyncIterator[bytes], bucket_name: str, key_name: str) -> bool:
        async with self.session.client('s3') as s3_client:
            response = await s3_client.create_multipart_upload(Bucket=bucket_name, Key=key_name)
            upload_id = response['UploadId']
            part_number = 1
            parts = []
            max_concurrency = 40

            async def upload_part(part_num, chunk):
                response = await s3_client.upload_part(
                    Bucket=bucket_name,
                    Key=key_name,
                    PartNumber=part_num,
                    UploadId=upload_id,
                    Body=chunk
                )
                return {"ETag": response["ETag"], "PartNumber": part_num}

            try:
                tasks = []
                async for chunk in byte_stream:
                    if len(tasks) >= max_concurrency:
                        parts.extend(await asyncio.gather(*tasks))
                        tasks = []
                    tasks.append(upload_part(part_number, chunk))
                    part_number += 1
                if tasks:
                    parts.extend(await asyncio.gather(*tasks))

                await s3_client.complete_multipart_upload(
                    Bucket=bucket_name,
                    Key=key_name,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts}
                )
                print(f"Upload completed for {key_name}")
                return True

            except Exception as e:
                await s3_client.abort_multipart_upload(Bucket=bucket_name, Key=key_name, UploadId=upload_id)
                print(f"Upload failed: {e}")
                return False

    def upload_file_sync(self, file_data: bytes, bucket_name: str, key_name: str):
        self.sync_client.put_object(Bucket=bucket_name, Key=key_name, Body=file_data)
        print(f"File uploaded to {bucket_name}/{key_name} synchronously.")

    def get_file_sync(self, bucket_name: str, key_name: str) -> bytes:

        buffer = BytesIO()
        config = TransferConfig(multipart_threshold=10 * 1024 * 1024, max_concurrency=10)  # 10 MB threshold, 10 threads

        self.sync_client.download_fileobj(Bucket=bucket_name, Key=key_name, Fileobj=buffer, Config=config)
        buffer.seek(0)

        # response = self.sync_client.get_object(Bucket=bucket_name, Key=key_name)
        # file_data = response['Body'].read()
        print(f"File {key_name} downloaded from {bucket_name} synchronously.")
        # return file_data

        return buffer.getvalue()

    async def get_file_async(self, bucket_name: str, key_name: str, output_stream: BinaryIO):
        async with self.session.client('s3') as s3_client:
            metadata = await s3_client.head_object(Bucket=bucket_name, Key=key_name)
            file_size = metadata['ContentLength']

            chunk_size = 5 * 1024 * 1024  # 5 MB chunks
            num_parts = (file_size + chunk_size - 1) // chunk_size  # Ceil division for total parts
            max_concurrency = 40

            async def download_part(part_num: int):
                print(f"Downloading part {part_num} of {num_parts}")
                start = part_num * chunk_size
                end = min(start + chunk_size - 1, file_size - 1)
                range_header = f"bytes={start}-{end}"

                response = await s3_client.get_object(Bucket=bucket_name, Key=key_name, Range=range_header)
                part_data = await response['Body'].read()

                print(f"Completing part {part_num} of {num_parts}")

                output_stream.seek(start)
                output_stream.write(part_data)

            download_tasks = []

            for part_num in range(num_parts):
                if len(download_tasks) >= max_concurrency:
                    await asyncio.gather(*download_tasks)
                    download_tasks = []
                download_tasks.append(download_part(part_num))

            # Run remaining tasks
            if download_tasks:
                await asyncio.gather(*download_tasks)

            output_stream.seek(0)  # Reset stream position if needed
            print(f"File {key_name} downloaded asynchronously to output stream.")

    def list_files(self, bucket_name: str, prefix: Optional[str] = None, page_number: int = 1, page_size: int = 100) -> List[str]:
        paginator = self.sync_client.get_paginator("list_objects_v2")
        operation_params = {"Bucket": bucket_name}
        if prefix:
            operation_params["Prefix"] = prefix

        file_keys = []
        page_index = 0
        for page in paginator.paginate(**operation_params, PaginationConfig={"PageSize": page_size}):
            page_index += 1
            if page_index == page_number:
                # Only return keys from the specified page
                if "Contents" in page:
                    file_keys.extend([obj["Key"] for obj in page["Contents"]])
                break

        # Return the list of file keys from the requested page or an empty list if page is out of bounds
        return file_keys

    # Delete a file
    def delete_file(self, bucket_name: str, key_name: str):
        self.sync_client.delete_object(Bucket=bucket_name, Key=key_name)
        print(f"File {key_name} deleted from {bucket_name}.")

    # Get file metadata
    def get_file_metadata(self, bucket_name: str, key_name: str) -> Dict[str, str]:
        response = self.sync_client.head_object(Bucket=bucket_name, Key=key_name)

        metadata = {
            "ContentLength": response.get("ContentLength"),  # Size in bytes
            "LastModified": response.get("LastModified"),  # Last modified timestamp
            "ContentType": response.get("ContentType"),  # MIME type
            "ETag": response.get("ETag"),  # Entity tag, a unique identifier for the object
            **response.get("Metadata", {})  # Custom metadata, if any
        }
        return metadata

# async def example_byte_stream():
#     for i in range(5):
#         await asyncio.sleep(1)
#         yield b"Data chunk " + str(i).encode()
#
# # Instantiate and use S3Impl
# s3_impl = S3Impl('your_access_key', 'your_secret_key', 'your_region')
# bucket = 'your_bucket_name'
#
# # Example synchronous usage
# s3_impl.upload_file_sync('local_file.txt', bucket, 'key_name')
# s3_impl.get_file_sync(bucket, 'key_name', 'downloaded_file.txt')
# file_list = s3_impl.list_files(bucket, 'optional_prefix/')
# print("Files in bucket:", file_list)
# s3_impl.delete_file(bucket, 'key_name')
# metadata = s3_impl.get_file_metadata(bucket, 'key_name')
# print("Metadata for file:", metadata)
#
# # Example asynchronous usage
# asyncio.run(s3_impl.upload_stream(example_byte_stream(), bucket, 'async_key_name'))
# asyncio.run(s3_impl.get_file_async(bucket, 'async_key_name', 'async_downloaded_file.txt'))

# async def example_byte_stream():
#     for i in range(5):
#         await asyncio.sleep(1)  # Simulate delay in receiving data
#         yield b"Data chunk " + str(i).encode()

# s3_impl = S3Impl('your_access_key', 'your_secret_key', 'your_region')
# asyncio.run(s3_impl.upload_stream(example_byte_stream(), 'your_bucket_name', 'your_key_name'))
