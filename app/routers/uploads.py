import os
import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from typing import List
from app.models.schemas import FileUploadResponse
from app.database import get_supabase
from app.services.document_processor import extract_text_from_file
from app.services.ai_analyzer import analyze_text_with_openai

router = APIRouter(prefix="/uploads", tags=["uploads"])

TEMP_UPLOAD_DIR = "temp_uploads"
logger = logging.getLogger(__name__)

def ensure_temp_dir():
    if not os.path.exists(TEMP_UPLOAD_DIR):
        os.makedirs(TEMP_UPLOAD_DIR)
        logger.info(f"Created temporary upload directory: {TEMP_UPLOAD_DIR}")

def process_file_in_background(
    file_id: str,
    temp_file_path: str,
    original_filename: str,
    supabase
):
    logger.info(f"=== Starting background task for file_id: {file_id} ===")
    try:
        if not os.path.exists(temp_file_path):
            raise FileNotFoundError(f"Temporary file not found: {temp_file_path}")
        logger.info(f"Starting text extraction for file: {original_filename}")
        extracted_text = extract_text_from_file(temp_file_path, original_filename)
        logger.info(f"Text extraction completed. Extracted {len(extracted_text)} characters")
        # --- AI Analysis Step ---
        try:
            logger.info("Starting AI analysis...")
            ai_result = analyze_text_with_openai(extracted_text)
            summary = ai_result.get("summary", "")
            keywords = ai_result.get("keywords", [])
            logger.info(f"AI analysis completed. Summary length: {len(summary)}, Keywords: {keywords}")
            # Insert into ai_analysis_results
            logger.info("Inserting AI analysis results into database...")
            result = supabase.table("ai_analysis_results").insert({
                "file_id": file_id,
                "summary": summary,
                "keywords": keywords
            }).execute()
            logger.info(f"Database insert result: {result}")
        except Exception as ai_error:
            logger.error(f"Error during AI analysis: {str(ai_error)}", exc_info=True)
        # Save to report_content table
        logger.info("Saving extracted text to report_content table...")
        report_content = {
            "file_id": file_id,
            "extracted_text": extracted_text,
            "extraction_date": datetime.utcnow().isoformat()
        }
        result = supabase.table("report_content").insert(report_content).execute()
        logger.info(f"Report content insert result: {result}")
        # Update file status
        logger.info("Updating file status to 'processed'...")
        result = supabase.table("file_uploads").update({"status": "processed"}).eq("id", file_id).execute()
        logger.info(f"Status update result: {result}")
    except Exception as e:
        logger.error(f"Error in background task: {str(e)}", exc_info=True)
        try:
            supabase.table("file_uploads").update({"status": "error"}).eq("id", file_id).execute()
        except Exception as db_error:
            logger.error(f"Failed to update error status: {str(db_error)}")
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
        except Exception as cleanup_error:
            logger.error(f"Failed to clean up temporary file: {str(cleanup_error)}")
    logger.info(f"=== Completed background task for file_id: {file_id} ===")

@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = None,
    supabase = Depends(get_supabase)
):
    logger.info(f"=== Starting file upload for: {file.filename} ===")
    try:
        ensure_temp_dir()
        temp_file_path = os.path.join(TEMP_UPLOAD_DIR, file.filename)
        # Save file to temp directory
        logger.info(f"Saving file to temporary location: {temp_file_path}")
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.info(f"File saved successfully. Size: {len(content)} bytes")
        # Create file_uploads record
        file_upload = {
            "filename": file.filename,
            "file_size": len(content),
            "file_type": file.content_type,
            "content_type": file.content_type,
            "upload_path": f"uploads/{file.filename}",  # For DB
            "status": "pending",
            "user_id": user_id,
            "upload_timestamp": datetime.utcnow().isoformat()
        }
        logger.info("Creating file_uploads record...")
        db_response = supabase.table("file_uploads").insert(file_upload).execute()
        if not db_response.data:
            raise HTTPException(status_code=400, detail="Failed to create file record")
        file_id = db_response.data[0]["id"]
        logger.info(f"File record created with ID: {file_id}")
        # Start background task
        logger.info("Adding background task...")
        background_tasks.add_task(
            process_file_in_background,
            file_id,
            temp_file_path,
            file.filename,
            supabase
        )
        logger.info("Background task added successfully")
        return FileUploadResponse(**db_response.data[0])
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}", exc_info=True)
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