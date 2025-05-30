from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrganizationCreate(BaseModel):
    name: str

class Organization(BaseModel):
    id: str
    name: str
    created_at: datetime

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    status: str
    created_at: datetime 