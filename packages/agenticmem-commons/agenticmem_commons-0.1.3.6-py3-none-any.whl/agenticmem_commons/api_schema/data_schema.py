from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    message: str
    s3_paths: list[str]
