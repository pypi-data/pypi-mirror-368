import json
import os
from io import BytesIO
from typing import Dict, Optional, AsyncIterator

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from vital_ai_domain.model.FileNode import FileNode
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.service.graph.virtuoso_service import VirtuosoGraphService
from vital_ai_vitalsigns.service.vital_service import VitalService
from vital_ai_vitalsigns.vitalsigns import VitalSigns
from kgraphservice.binary.s3_impl import S3Impl
from kgraphservice.config.config_utils import ConfigUtils
from kgraphservice.rest.impl.kgraphservice_rest_impl import KGraphServiceRESTImpl
from kgraphservice.rest_binary.impl.kgraphservice_rest_binary_impl import KGraphServiceRESTBinaryImpl
from fastapi import FastAPI, UploadFile, HTTPException, Form, File, Depends
from fastapi.responses import StreamingResponse
from kgraphservice.rest_binary.model.file_metadata import FileMetadata
from kgraphservice.rest_binary.model.file_request import FileRequest
from kgraphservice.rest_binary.model.list_files_request import ListFilesRequest
from kgraphservice.rest_binary.model.status_response import StatusResponse, StatusType, StatusType_OK

vital_home = os.getenv('VITAL_HOME', '')
print(f"VITAL_HOME: {vital_home}")

app = FastAPI()

vs = VitalSigns()

vitalhome = vs.get_vitalhome()

config = vs.get_config()

print(config)

vitalservice_config = config.vitalservice_list[0]

virtuoso_username = vitalservice_config.graph_database.username
virtuoso_password = vitalservice_config.graph_database.password
virtuoso_endpoint = vitalservice_config.graph_database.endpoint

virtuoso_graph_service = VirtuosoGraphService(
    username=virtuoso_username,
    password=virtuoso_password,
    endpoint=virtuoso_endpoint,

    base_uri="http://vital.ai",
    namespace="graph"
)

vital_service = VitalService(
    vitalservice_name=vitalservice_config.name,
    vitalservice_namespace=vitalservice_config.namespace,
    graph_service=virtuoso_graph_service,
)

rest_impl = KGraphServiceRESTImpl(
    vitalservice=vital_service
)

kgraphservice_config = ConfigUtils.load_config(vitalhome)

aws_access_key_id = kgraphservice_config["kgraphservice_binary"].get("aws_access_key_id", "")
aws_secret_access_key = kgraphservice_config["kgraphservice_binary"].get("aws_secret_access_key", "")
region_name = kgraphservice_config["kgraphservice_binary"].get("region_name", "")
bucket_name_config = kgraphservice_config["kgraphservice_binary"].get("bucket_name", "")


s3_impl = S3Impl(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name)

# from vitalsigns config
org_id = "haley.ai"
app_id = "chat-saas"

kgraphservice_binary_impl = KGraphServiceRESTBinaryImpl(
    impl=s3_impl,
    org_id=org_id,
    app_id=app_id,
    vitalservice=vital_service
)


def get_kgraphservice_binary():
    return kgraphservice_binary_impl


def get_bucket_name():
    return bucket_name_config


class DictEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return super().default(obj)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# override any validation errors for custom response
@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def custom_validation_exception_handler(request: Request, exc: ValidationError):

    print(request)

    errors = exc.errors()

    print(errors)

    custom_errors = [
        {
            "loc": error["loc"],
            "msg": error["msg"],
        }
        for error in errors
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": custom_errors}
    )


@app.post("/kgraphservice")
async def handle_kgraphservice_request(request: Request):

    request_data = await request.json()

    print(request_data)

    response = rest_impl.handle_request(request_data)

    # print(response)

    json_response = json.dumps(response, cls=DictEncoder)

    return JSONResponse(content=json_response )


async def file_to_async_iterator(file: UploadFile, chunk_size: int = 8192) -> AsyncIterator[bytes]:
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        yield chunk


@app.post("/kgraphservice-binary")
async def handle_kgraphservice_binary_request(
        request: str = Body(...),
        file: Optional[UploadFile] = File(None),
        kgraphservice_binary: KGraphServiceRESTBinaryImpl = Depends(get_kgraphservice_binary)
):

    print(request)

    request_dict = json.loads(request)

    if file is not None:
        # add or update case will handle file upload
        pass

    kgraphservice_binary_class = request_dict.get("kgraphservice_binary_class", None)

    account_uri: str = request_dict.get("account_uri", None)

    if kgraphservice_binary_class == "AddFileNode":

        file_node_dict = request_dict.get("file_node", None)

        file_node: FileNode = GraphObject.from_json_map(file_node_dict)

        if not file:
            # error case
            pass

        bucket_name = get_bucket_name()

        add_status = await kgraphservice_binary.add_filenode(
            bucket_name=bucket_name,
            account_uri=account_uri,
            filenode=file_node,
            file=file)

    if kgraphservice_binary_class == "GetFileNode":

        file_node_uri: str = request_dict.get("file_node_uri", None)

        file_node_status = await kgraphservice_binary.get_filenode(
            account_uri=account_uri,
            filenode_uri=file_node_uri)

    if kgraphservice_binary_class == "DeleteFileNode":

        file_node_uri: str = request_dict.get("file_node_uri", None)

        delete_status = await kgraphservice_binary.delete_filenode(
            account_uri=account_uri,
            filenode_uri=file_node_uri)

    if kgraphservice_binary_class == "UpdateFileNode":

        file_node: FileNode = request_dict.get("file_node", None)

        if file:
            data_iter = file_to_async_iterator(file)
        else:
            data_iter = None

        update_status = await kgraphservice_binary.update_filenode(
            account_uri=account_uri,
            filenode=file_node,
            data=data_iter)

    if kgraphservice_binary_class == "GetFileNodeMetadata":

        file_node_uri: str = request_dict.get("file_node_uri", None)

        file_node_metadata_status = await kgraphservice_binary.get_filenode_metadata(
            account_uri=account_uri,
            filenode_uri=file_node_uri)

    # print(response)

    response = StatusResponse(
        kgraphservice_binary_class="StatusResponse",
        status=StatusType_OK,
        status_code=0,
        status_message="ok"
    )

    json_response = json.dumps(response, cls=DictEncoder)

    return JSONResponse(content=json_response )


@app.post("/kgraphservice-upload-async")
async def upload_file_async(
    metadata: str = Form(...),  # Metadata in JSON format
    file: UploadFile = File(...),
    kgraphservice_binary: KGraphServiceRESTBinaryImpl = Depends(get_kgraphservice_binary)
):
    try:
        file_metadata = json.loads(metadata)

        key_name = f"{file.filename}"

        bucket_name = get_bucket_name()

        min_chunk_size = 5 * 1024 * 1024
        buffer = await file.read(min_chunk_size)

        if len(buffer) < min_chunk_size:
            kgraphservice_binary.upload_file_sync(buffer, bucket_name, key_name)
        else:
            async def file_byte_stream():
                yield buffer  # Yield the initial 5 MB chunk
                while chunk := await file.read(min_chunk_size):
                    yield chunk

            await kgraphservice_binary.upload_file_async(file_byte_stream(), bucket_name, key_name)

        print(f"Uploaded Async: {file.filename}")

        return {
            "message": f"File '{file.filename}' uploaded asynchronously",
            "key_name": key_name,
            "metadata": file_metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kgraphservice-download-async/")
async def download_file_async(
    metadata: str = Form(...),
    kgraphservice_binary: KGraphServiceRESTBinaryImpl = Depends(get_kgraphservice_binary)
):
    try:
        file_request = json.loads(metadata)
        key_name = file_request['key_name']
        bucket_name = get_bucket_name()

        # Get the output stream containing the file data
        output_stream = await kgraphservice_binary.download_file_async(bucket_name, key_name)

        # Async generator to yield chunks from BytesIO
        async def file_chunk_generator(buffer):
            buffer.seek(0)
            while chunk := buffer.read(8192):  # 8 KB chunks
                yield chunk

        # Return the StreamingResponse using the generator
        return StreamingResponse(
            file_chunk_generator(output_stream),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_request['key_name']}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kgraphservice-upload-sync/")
async def upload_file_sync(
        metadata: str = Form(...),
        file: UploadFile = File(...),
        kgraphservice_binary: KGraphServiceRESTBinaryImpl = Depends(get_kgraphservice_binary)
):
    try:
        file_metadata = json.loads(metadata)
        key_name = f"{file.filename}"

        print(f"Upload Sync: {file.filename}")

        file_data = await file.read()

        bucket_name = get_bucket_name()
        kgraphservice_binary.upload_file_sync(file_data, bucket_name, key_name, metadata=file_metadata)

        return {"message": f"File '{file.filename}' uploaded synchronously", "key_name": key_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kgraphservice-download-sync/")
async def download_file_sync(request = Body(...), kgraphservice_binary: KGraphServiceRESTBinaryImpl = Depends(get_kgraphservice_binary)):
    try:
        bucket_name = get_bucket_name()
        print(f"Download Sync: {request}")
        file_data = kgraphservice_binary.download_file_sync(bucket_name, request["key_name"])
        return StreamingResponse(BytesIO(file_data), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={request['key_name']}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kgraphservice-list-files/")
async def list_files(request = Body(...), kgraphservice_binary: KGraphServiceRESTBinaryImpl = Depends(get_kgraphservice_binary)):
    try:
        bucket_name = get_bucket_name()
        print(f"List files: {request}")
        file_list = kgraphservice_binary.list_files(bucket_name=bucket_name, prefix=request.get("prefix"))
        return {"files": file_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/kgraphservice-delete-file/{key_name}")
async def delete_file(key_name: str, kgraphservice_binary: KGraphServiceRESTBinaryImpl = Depends(get_kgraphservice_binary)):
    try:
        bucket_name = get_bucket_name()
        print(f"Delete File: {key_name}")
        kgraphservice_binary.delete_file(bucket_name, key_name)
        return {"message": f"File '{key_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kgraphservice-file-metadata/")
async def get_file_metadata(request = Body(...), kgraphservice_binary: KGraphServiceRESTBinaryImpl = Depends(get_kgraphservice_binary)):
    try:
        bucket_name = get_bucket_name()
        metadata = kgraphservice_binary.get_file_metadata(bucket_name, request["key_name"])
        return {"metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_app(*, host: str = "0.0.0.0", port:int = 6008):
    uvicorn.run(app, host=host, port=port)

