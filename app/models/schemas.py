from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrganizationCreate(BaseModel):
    name: str

class Organization(BaseModel):
    id: str
    name: str
    created_at: datetime

class FileUploadCreate(BaseModel):
    filename: str
    file_size: int
    content_type: str
    status: str = "pending"
    user_id: Optional[str] = None

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    content_type: str
    status: str
    user_id: Optional[str] = None
    upload_timestamp: Optional[datetime] = None

class ReportContentCreate(BaseModel):
    file_id: str
    extracted_text: str
    extraction_date: datetime 