from fastapi import HTTPException, Request, status


def get_filename_and_type(request: Request):
    try:
        content_disposition = request.headers.get("Content-Disposition")
        filename_unformatted = content_disposition.split("filename=")[1]
        filename = filename_unformatted.split('"')[1]
        content_type = request.headers.get("File-Type")
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Missing required headers, or formatted incorrectly. {dir(request.headers)}")
    return filename, content_type
