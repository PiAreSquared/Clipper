from fastapi.testclient import TestClient
from main import app
import io
import random
import os

client = TestClient(app)


class MockFile(io.BytesIO):
    def __init__(self, total_size, chunk_size=1024):
        super().__init__()
        self.total_size = total_size
        self.chunk_size = chunk_size
        self.data = None  # Pre-generate random data
        self.read_count = 0

    def read(self, size):
        if self.data is None:
            self.data = bytes(random.randrange(256) for _ in range(self.total_size))
        if self.read_count + size > self.total_size:
            size = self.total_size - self.read_count
        if not size:
            return b""  # Return empty bytes when reaching end
        data = self.data[self.read_count:self.read_count + size]
        self.read_count += size
        return data

    def tell(self):
        return self.read_count

    def seek(self, offset, whence=0):
        if whence == io.SEEK_SET:
            self.read_count = offset
        elif whence == io.SEEK_CUR:
            self.read_count += offset
        elif whence == io.SEEK_END:
            self.read_count = self.total_size - offset
        else:
            raise ValueError("Invalid whence")


def test_root():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_upload_valid_video_file():
    # Create a sample video file for testing
    file_content = b"Sample video content"
    files = {"file": ("test_file.mp4", file_content, "video/mp4")}
    headers = {
        "Content-Type": "multipart/form-data; boundary=--------------------------",
        "File-Type": "video/mp4",
        "Content-Disposition": 'attachment; filename="test_file.mp4"'
    }

    with client.stream("POST", "/upload", files=files, headers=headers) as response:
        response.read()
        assert response.status_code == 200
        assert response.json()["filename"] == "test_file.mp4"

        filepath = response.json()["filepath"]

    with open(filepath, "r") as f:
        assert f.read() == file_content.decode("utf-8")


def test_upload_file_size_limit_exceeded():
    # Create a large file (exceeding the size limit)
    # file_content = b"Large file content" * 1024 * 1024 * 1024  # 1GB file
    # files = {"file": ("large_file.txt", file_content, "video/mp4")}
    # check if file exists
    if not os.path.exists("test.mp4"):
        return 
    files = {"file": open("test.mp4", "rb")}
    # stream = __import__("io").BytesIO(b"Large file content" * 100)
    # add to stream every time data is read
    # stream.read = lambda n: os.urandom(n)
    # files = {"file": ("large_file.txt", MockFile(round(MAX_FILE_SIZE * 1.1)), "video/mp4")}
    headers = {
        "Content-Type": "multipart/form-data; boundary=--------------------------",
        "File-Type": "video/mp4",
        "Content-Disposition": 'attachment; filename="large_file.txt"'
    }

    response = client.post("/upload", files=files, headers=headers)
    response.read()
    assert response.status_code == 413
    assert "exceeds the maximum limit of" in response.text


def test_upload_file_invalid_type():
    # Create a file with an invalid type
    file_content = b"Invalid file content"
    file_type = "application/pdf"
    files = {"file": ("invalid_file.pdf", file_content, file_type)}
    headers = {
        "Content-Type": "multipart/form-data; boundary=--------------------------",
        "File-Type": file_type,
        "Content-Disposition": 'attachment; filename="invalid_file.pdf"'
    }

    with client.stream("POST", "/upload", files=files, headers=headers) as response:
        response.read()
        assert response.status_code == 415
        assert f"'{file_type}' is not supported" in response.text

# Run the tests
# To run the tests, you can use the following command in the terminal:
# $ pytest api/test_main.py
#
