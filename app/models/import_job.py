from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from ..database import Base


class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, nullable=False, index=True)  # Celery task ID
    filename = Column(String(255), nullable=False)
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, processing, completed, failed
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    result_summary = Column(JSON, nullable=True)  # Detailed results
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ImportJob(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"