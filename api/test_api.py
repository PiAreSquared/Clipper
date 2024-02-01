from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

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
    
# def test_upload_file_size_limit_exceeded():
#     # Create a large file (exceeding the size limit)
#     # file_content = b"Large file content" * 1024 * 1024 * 1024  # 1GB file
#     # files = {"file": ("large_file.txt", file_content, "video/mp4")}
#     files = {"file": open("/dev/urandom", "rb")}
#     headers = {
#         "Content-Type": "multipart/form-data; boundary=--------------------------", 
#         "File-Type": "video/mp4", 
#         "Content-Disposition": 'attachment; filename="large_file.txt"'
#     }
    
#     with client.stream("POST", "/upload", files=files, headers=headers) as response:
#         response.read()
#         assert response.status_code == 413
#         assert "exceeds the maximum limit of" in response.text

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


