from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class ImportJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: str
    filename: str
    total_records: int
    processed_records: int
    successful_records: int
    failed_records: int
    status: str
    progress_percentage: int
    error_message: Optional[str]
    result_summary: Optional[Dict[str, Any]]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class ImportProgressResponse(BaseModel):
    task_id: str
    status: str
    progress_percentage: int
    processed_records: int
    total_records: int
    successful_records: int
    failed_records: int
    error_message: Optional[str]
    estimated_time_remaining: Optional[int]  # seconds


class ImportSummaryResponse(BaseModel):
    total_processed: int
    successful_imports: int
    failed_imports: int
    duplicates_overwritten: int
    validation_errors: int
    processing_time_seconds: float
    errors: Optional[list[str]]