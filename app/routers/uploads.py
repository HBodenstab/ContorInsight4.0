import os
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends, Form
from typing import List
from app.models.schemas import FileUploadResponse, FileUploadCreate, ReportContentCreate
from app.database import get_supabase
from datetime import datetime
from app.services.document_processor import extract_text_from_file

router = APIRouter(prefix="/uploads", tags=["uploads"])

TEMP_UPLOAD_DIR = "temp_uploads"

def ensure_temp_dir():
    if not os.path.exists(TEMP_UPLOAD_DIR):
        os.makedirs(TEMP_UPLOAD_DIR)

def process_file_in_background(
    file_id: str,
    temp_file_path: str,
    original_filename: str,
    supabase
):
    try:
        extracted_text = extract_text_from_file(temp_file_path, original_filename)
        # Save to report_content table
        report_content = {
            "file_id": file_id,
            "extracted_text": extracted_text,
            "extraction_date": datetime.utcnow().isoformat()
        }
        supabase.table("report_content").insert(report_content).execute()
        # Update file_uploads status
        supabase.table("file_uploads").update({"status": "processed"}).eq("id", file_id).execute()
    except Exception as e:
        supabase.table("file_uploads").update({"status": "failed"}).eq("id", file_id).execute()
        print(f"Text extraction failed for file_id {file_id}: {e}")
    finally:
        # Clean up temp file
        try:
            os.remove(temp_file_path)
        except Exception:
            pass

@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = None,
    supabase = Depends(get_supabase)
):
    ensure_temp_dir()
    temp_file_path = os.path.join(TEMP_UPLOAD_DIR, file.filename)
    # Save file to temp directory
    with open(temp_file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    # Create file_uploads record
    file_upload = {
        "filename": file.filename,
        "file_size": len(content),
        "file_type": file.content_type,  # For DB compatibility
        "content_type": file.content_type,  # For Pydantic model compatibility
        "status": "pending",
        "user_id": user_id,
        "upload_timestamp": datetime.utcnow().isoformat(),
        "upload_path": f"uploads/{file.filename}"
    }
    db_response = supabase.table("file_uploads").insert(file_upload).execute()
    if not db_response.data:
        raise HTTPException(status_code=400, detail="Failed to create file record")
    file_id = db_response.data[0]["id"]
    # Start background task
    background_tasks.add_task(
        process_file_in_background,
        file_id,
        temp_file_path,
        file.filename,
        supabase
    )
    return FileUploadResponse(**db_response.data[0])

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