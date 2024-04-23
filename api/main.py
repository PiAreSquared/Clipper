import boto3.exceptions
from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.requests import ClientDisconnect
import uuid

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.validators import MaxSizeValidator, ValidationError
from streaming_form_data.targets import FileTarget, ValueTarget

from exceptions import FileLimitExceededException, FileTypeUnsupportedException
from upload_file import get_filename_and_type
from highlights_clipper import clip_video
from overlay_commentary import main as overlay_commentary
from constants import MAX_FILE_SIZE, ALLOWED_FILE_TYPES

from mangum import Mangum
import boto3
import os
import io

# Configure your AWS credentials and region
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-2')
S3_BUCKET_UNPROCESSED_VIDS_NAME = os.environ.get('UNPROCESSED_BUCKET_NAME', 'unproccessed-games')
S3_BUCKET_PROCESSED_VIDS_NAME = os.environ.get('PROCESSED_BUCKET_NAME', 'processed-games')
S3_BUCKET_PROCESSED_COMM_VIDS_NAME = os.environ.get('COMM_BUCKET_NAME', 'processed-commentary-games')


my_config = boto3.session.Config(
    region_name=AWS_REGION,
    signature_version='v4',
    # aws_access_key_id=os.environ.get('AWS_ACCESS_KY_ID'),
    # aws_secret_access_key=os.environ.get('AWS_ACCESS_SECRET_KEY'),
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)
s3_client = boto3.client('s3', config=my_config)

app = FastAPI()
handler = Mangum(app)

class MaxFileSizeValidator(object):
    def __init__(self, max_size=MAX_FILE_SIZE):
        self.current_size = 0
        self.max_size = max_size

    def __call__(self, chunk_size: int):
        self.current_size += chunk_size
        if self.current_size > self.max_size:
            raise FileLimitExceededException(size=self.current_size, max_size=MAX_FILE_SIZE)


@app.exception_handler(FileLimitExceededException)
async def file_limit_exceeded_exception_handler(request, exc: FileLimitExceededException):
    return Response(status_code=413, content=str(exc))


@app.exception_handler(FileTypeUnsupportedException)
async def file_type_not_supported_exception_handler(request, exc: FileTypeUnsupportedException):
    return Response(status_code=415, content=str(exc))


@app.get("/hello")
def hello():
    return {"message": "Hello World"}

@app.get("/fetch/unprocessed_video")
async def fetch_unprocessed_video(request: Request):
    filename = request.query_params.get("filename")
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is missing.")

    try:
        s3_client.head_object(Bucket=S3_BUCKET_UNPROCESSED_VIDS_NAME, Key=filename)
        response = s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET_UNPROCESSED_VIDS_NAME, 'Key': filename}, ExpiresIn=3600)

        return {"url": response}

    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'There was an error fetching the file. Please try again. {e}')

@app.get("/fetch/processed_video")
async def fetch_processed_video(request: Request):
    filename = request.query_params.get("filename")
    commentary = True if request.query_params.get("commentary") else False
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is missing.")

    bucket = S3_BUCKET_PROCESSED_COMM_VIDS_NAME if commentary else S3_BUCKET_PROCESSED_VIDS_NAME

    try:
        response = s3_client.head_object(Bucket=bucket, Key=filename)
        response = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': filename}, ExpiresIn=3600)

        return {"url": response}

    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'There was an error fetching the file. Please try again. {e}')

@app.post("/clip")
async def clip_vid(request: Request):
    options = await request.json()
    print(options)
    filename = options.get("filename")
    include_commentary = options.get("include_commentary", "False")
    if not include_commentary or include_commentary.lower() == "false":
        include_commentary = False
    else:
        include_commentary = True
    clip_length = options.get("clip_length", 15)
    number_of_clips = options.get("number_of_clips", 15)

    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is missing.")
    
    try:
        print("Clipping the video.")
        clip_video(s3_client, S3_BUCKET_UNPROCESSED_VIDS_NAME, filename, clip_length, number_of_clips)
        print("Video clipped successfully.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'There was an error processing the file. Please try again. {e}')
    
    if not include_commentary:
        return {"message": "Video clipped successfully."}
    
    try:
        print("Adding commentary to the video.")
        s3_client.download_file(S3_BUCKET_UNPROCESSED_VIDS_NAME, "crowdnoise.mp3", "/tmp/crowdnoise.mp3")
        overlay_commentary("/tmp/output.mp4", "/tmp/output_comm.mp4", "/tmp/crowdnoise.mp3")
        s3_client.upload_file("/tmp/output_comm.mp4", S3_BUCKET_PROCESSED_COMM_VIDS_NAME, filename)
        print("Commentary added successfully.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'There was an error processing the file. Please try again. {e}')
    
    return {"message": "Video clipped with commentary successfully."}

@app.get("/status")
async def get_status(request: Request):
    filename = request.query_params.get("filename")
    in_unprocessed_bucket = False
    in_processed_bucket = False
    in_comm_bucket = False

    try:
        s3_client.head_object(Bucket=S3_BUCKET_UNPROCESSED_VIDS_NAME, Key=filename)
        in_unprocessed_bucket = True
    except s3_client.exceptions.NoSuchKey:
        pass
    except boto3.exceptions.botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] != "404":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f'There was an error fetching the file. Please try again. {e}')
        

    if not in_unprocessed_bucket:
        return {"status": "File not found.", "progress": "UPLOADING"}
    
    try:
        s3_client.head_object(Bucket=S3_BUCKET_PROCESSED_VIDS_NAME, Key=filename)
        in_processed_bucket = True
    except s3_client.exceptions.NoSuchKey:
        pass
    except boto3.exceptions.botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] != "404":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f'There was an error fetching the file. Please try again. {e}')
        

    if not in_processed_bucket:
        return {"status": "File uploaded.", "progress": "UPLOADED"}
    
    try:
        s3_client.head_object(Bucket=S3_BUCKET_PROCESSED_COMM_VIDS_NAME, Key=filename)
        in_comm_bucket = True
    except s3_client.exceptions.NoSuchKey:
        pass
    except boto3.exceptions.botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] != "404":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f'There was an error fetching the file. Please try again. {e}')
        

    if not in_comm_bucket:
        return {"status": "File processed.", "progress": "CLIPPED"}
    
    return {"status": "File processed with commentary.", "progress": "CLIPPED_WITH_COMMENTARY"}

@app.get("/start_upload")
async def start_upload(request: Request):
    print("/start_upload request: ", request.query_params)
    filename = request.query_params.get("filename")

    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is missing.")
    
    try:
        s3_object_key = f"{uuid.uuid4()}-{filename}"
        print("s3_object_key: ", s3_object_key)
        response = s3_client.create_multipart_upload(Bucket=S3_BUCKET_UNPROCESSED_VIDS_NAME, Key=s3_object_key)
        upload_id = response["UploadId"]
        return {"upload_id": upload_id, "key": s3_object_key}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'There was an error processing the file. Please try again. {e}')

@app.post("/upload")
async def upload_file(request: Request):
    # Process the uploaded file here
    # check file type, size, etc.
    filename, content_type = get_filename_and_type(request)

    if content_type not in ALLOWED_FILE_TYPES:
        raise FileTypeUnsupportedException(content_type=content_type)

    try:
        filepath = f"/tmp/{uuid.uuid4()}-{filename}"
        size_validator = MaxFileSizeValidator(MAX_FILE_SIZE + 1024)
        file_target = FileTarget(filepath, validator=MaxSizeValidator(MAX_FILE_SIZE))
        data = ValueTarget()

        parser = StreamingFormDataParser(headers=request.headers)
        parser.register("file", file_target)
        parser.register("data", data)

        async for chunk in request.stream():
            size_validator(len(chunk))
            parser.data_received(chunk)

    except ClientDisconnect:
        raise HTTPException(status_code=status.HTTP_499_CLIENT_CLOSED_REQUEST,
                            detail="Client disconnected while uploading file.")
    except FileLimitExceededException as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'There was an error processing the file. Please try again. {e}')

    if not file_target.multipart_filename:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File is missing.")

    # Process the file content here
    # Save the file to disk, etc.

    return {"filename": filename, "filepath": filepath, "file_size": size_validator.current_size}
