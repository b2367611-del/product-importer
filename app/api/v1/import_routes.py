from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
from datetime import datetime

from ...database import get_db
from ...models import ImportJob
from ...schemas import ImportJobResponse, ImportProgressResponse
from ...tasks import import_csv_task
from ...config import settings


router = APIRouter(prefix="/import", tags=["import"])


@router.post("/upload", response_model=ImportJobResponse)
async def upload_csv_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload CSV file for product import."""
    
    # Validate file type
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
        )
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Generate temporary task ID
    temp_task_id = f"temp_{uuid.uuid4()}"
    
    # Create import job record
    import_job = ImportJob(
        task_id=temp_task_id,
        filename=file.filename,
        status="pending"
    )
    db.add(import_job)
    db.commit()
    db.refresh(import_job)
    
    # Start import task
    task = import_csv_task.delay(file_path, import_job.id)
    
    # Update job with actual task ID
    import_job.task_id = task.id
    db.commit()
    
    return import_job


@router.get("/progress/{task_id}", response_model=ImportProgressResponse)
def get_import_progress(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get import progress by task ID."""
    
    # Get import job
    import_job = db.query(ImportJob).filter(ImportJob.task_id == task_id).first()
    if not import_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found"
        )
    
    # Get task result
    from ...celery import celery_app
    task = celery_app.AsyncResult(task_id)
    
    # Calculate estimated time remaining with null checks
    estimated_time_remaining = None
    try:
        if (import_job.status == "processing" and 
            import_job.processed_records and import_job.processed_records > 0 and
            import_job.started_at and import_job.total_records):
            
            elapsed_time = (datetime.utcnow() - import_job.started_at).total_seconds()
            if elapsed_time > 0:
                records_per_second = import_job.processed_records / elapsed_time
                remaining_records = import_job.total_records - import_job.processed_records
                if records_per_second > 0:
                    estimated_time_remaining = int(remaining_records / records_per_second)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Error calculating ETA: {e}")
        estimated_time_remaining = None
    
    return ImportProgressResponse(
        task_id=task_id,
        status=import_job.status or "pending",
        progress_percentage=import_job.progress_percentage or 0,
        processed_records=import_job.processed_records or 0,
        total_records=import_job.total_records or 0,
        successful_records=import_job.successful_records or 0,
        failed_records=import_job.failed_records or 0,
        error_message=import_job.error_message,
        estimated_time_remaining=estimated_time_remaining
    )


@router.get("/jobs", response_model=List[ImportJobResponse])
def get_import_jobs(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of import jobs."""
    
    query = db.query(ImportJob)
    
    if status_filter:
        query = query.filter(ImportJob.status == status_filter)
    
    jobs = query.order_by(ImportJob.created_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get("/jobs/{job_id}", response_model=ImportJobResponse)
def get_import_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get specific import job details."""
    
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found"
        )
    
    return job