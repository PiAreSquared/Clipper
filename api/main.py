from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.requests import ClientDisconnect
import uuid

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.validators import MaxSizeValidator, ValidationError
from streaming_form_data.targets import FileTarget, ValueTarget

from exceptions import FileLimitExceededException, FileTypeUnsupportedException
from upload_file import get_filename_and_type


app = FastAPI()

MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
ALLOWED_FILE_TYPES = ["video/mp4", "video/quicktime"]


class MaxFileSizeValidator(object):
    def __init__(self, max_size=MAX_FILE_SIZE):
        self.current_size = 0
        self.max_size = max_size

    def __call__(self, chunk_size: int):
        self.current_size += chunk_size
        if self.current_size > self.max_size:
            raise FileLimitExceededException(max_size=MAX_FILE_SIZE)


@app.exception_handler(FileLimitExceededException)
async def file_limit_exceeded_exception_handler(request, exc: FileLimitExceededException):
    return Response(status_code=413, content=str(exc))


@app.exception_handler(FileTypeUnsupportedException)
async def file_type_not_supported_exception_handler(request, exc: FileTypeUnsupportedException):
    return Response(status_code=415, content=str(exc))


@app.get("/hello")
def hello():
    return {"message": "Hello World"}


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
