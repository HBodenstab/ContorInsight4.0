from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import List
from app.models.schemas import FileUploadResponse
from app.database import get_supabase
from datetime import datetime

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    organization_id: str = None,
    file_type: str = Form(...),
    supabase = Depends(get_supabase)
):
    file_content = await file.read()
    file_path = f"uploads/{file.filename}"
    
    try:
        # Upload to storage
        storage_response = supabase.storage.from_("uploads").upload(
            file_path,
            file_content,
            {"content-type": file.content_type}
        )
        
        # Create record in database
        file_record = {
            "filename": file.filename,
            "file_size": len(file_content),
            "status": "uploaded",
            "created_at": datetime.utcnow().isoformat(),
            "organization_id": organization_id,
            "file_type": file_type,
            "upload_path": file_path
        }
        
        db_response = supabase.table("file_uploads").insert(file_record).execute()
        
        if not db_response.data:
            raise HTTPException(status_code=400, detail="Failed to create file record")
            
        return FileUploadResponse(**db_response.data[0])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[FileUploadResponse])
async def list_uploads(supabase = Depends(get_supabase)):
    response = supabase.table("file_uploads").select("*").execute()
    return [FileUploadResponse(**upload) for upload in response.data]

@router.delete("/{file_id}")
async def delete_upload(file_id: str, supabase = Depends(get_supabase)):
    file_response = supabase.table("file_uploads").select("*").eq("id", file_id).execute()
    if not file_response.data:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_record = file_response.data[0]
    
    try:
        # Delete from storage
        supabase.storage.from_("uploads").remove([f"uploads/{file_record['filename']}"])
        
        # Delete from database
        supabase.table("file_uploads").delete().eq("id", file_id).execute()
        
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 