class FileLimitExceededException(Exception):
    MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024 # 5GB
    
    def __init__(self, size: int, max_size=MAX_FILE_SIZE):
        self.size = size
        self.max_size = max_size
    
    def __str__(self):
        return f"The file size of exceeds the maximum limit of {self.max_size / (1024 * 1024 * 1024)}GB."

class FileTypeNotSupportedException(Exception):
    def __init__(self, content_type: str):
        self.content_type = content_type
    
    def __str__(self):
        return f"File type '{self.content_type}' is not supported."