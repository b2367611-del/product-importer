from celery import current_task
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import pandas as pd
import time
import os
from typing import Dict, Any, List
from datetime import datetime

from ..celery import celery_app
from ..database import SessionLocal
from ..models import Product, ImportJob
from .webhook_tasks import trigger_webhook_task


@celery_app.task(bind=True, queue='upload_queue')
def import_csv_task(self, file_path: str, import_job_id: int) -> Dict[str, Any]:
    """
    Import products from CSV file with progress tracking.
    """
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Get import job
        import_job = db.query(ImportJob).filter(ImportJob.id == import_job_id).first()
        if not import_job:
            raise ValueError(f"Import job {import_job_id} not found")
        
        # Update job status
        import_job.status = "processing"
        import_job.started_at = datetime.utcnow()
        db.commit()
        
        # Read CSV file
        try:
            df = pd.read_csv(file_path)
            total_records = len(df)
            
            # Update total records
            import_job.total_records = total_records
            db.commit()
            
        except Exception as e:
            import_job.status = "failed"
            import_job.error_message = f"Failed to read CSV file: {str(e)}"
            import_job.completed_at = datetime.utcnow()
            db.commit()
            raise
        
        # Validate required columns
        required_columns = ['sku', 'name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns: {', '.join(missing_columns)}"
            import_job.status = "failed"
            import_job.error_message = error_msg
            import_job.completed_at = datetime.utcnow()
            db.commit()
            raise ValueError(error_msg)
        
        # Normalize column names and data
        df.columns = df.columns.str.lower().str.strip()
        df = df.fillna('')  # Replace NaN with empty strings
        
        # Statistics
        successful_count = 0
        failed_count = 0
        duplicate_overwrites = 0
        validation_errors = []
        batch_size = 1000
        
        # Process in batches
        for batch_start in range(0, total_records, batch_size):
            batch_end = min(batch_start + batch_size, total_records)
            batch_df = df.iloc[batch_start:batch_end]
            
            batch_results = process_product_batch(
                db, batch_df, validation_errors
            )
            
            successful_count += batch_results['successful']
            failed_count += batch_results['failed']
            duplicate_overwrites += batch_results['duplicates']
            
            # Update progress
            processed_records = batch_end
            progress_percentage = int((processed_records / total_records) * 100)
            
            import_job.processed_records = processed_records
            import_job.successful_records = successful_count
            import_job.failed_records = failed_count
            import_job.progress_percentage = progress_percentage
            db.commit()
            
            # Update Celery task state
            self.update_state(
                state='PROGRESS',
                meta={
                    'progress_percentage': progress_percentage,
                    'processed_records': processed_records,
                    'total_records': total_records,
                    'successful_records': successful_count,
                    'failed_records': failed_count
                }
            )
            
            # Small delay to prevent overwhelming the DB
            time.sleep(0.1)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Final update
        import_job.status = "completed"
        import_job.processed_records = total_records
        import_job.successful_records = successful_count
        import_job.failed_records = failed_count
        import_job.progress_percentage = 100
        import_job.completed_at = datetime.utcnow()
        import_job.result_summary = {
            'total_processed': total_records,
            'successful_imports': successful_count,
            'failed_imports': failed_count,
            'duplicates_overwritten': duplicate_overwrites,
            'validation_errors': len(validation_errors),
            'processing_time_seconds': round(processing_time, 2),
            'errors': validation_errors[:100]  # Limit error list
        }
        db.commit()
        
        # Clean up uploaded file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass  # Ignore cleanup errors
        
        # Trigger webhooks for successful import
        if successful_count > 0:
            trigger_webhook_task.apply_async(
                args=['import.completed', {
                    'import_job_id': import_job_id,
                    'total_processed': total_records,
                    'successful_imports': successful_count,
                    'failed_imports': failed_count,
                    'processing_time_seconds': processing_time
                }],
                queue='webhook_queue'
            )
        
        return {
            'status': 'completed',
            'total_processed': total_records,
            'successful_imports': successful_count,
            'failed_imports': failed_count,
            'duplicates_overwritten': duplicate_overwrites,
            'processing_time_seconds': processing_time
        }
        
    except Exception as e:
        # Handle any unexpected errors
        import_job.status = "failed"
        import_job.error_message = str(e)
        import_job.completed_at = datetime.utcnow()
        db.commit()
        
        # Clean up uploaded file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        
        raise
    
    finally:
        db.close()


def process_product_batch(db: Session, batch_df: pd.DataFrame, validation_errors: List[str]) -> Dict[str, int]:
    """Process a batch of products."""
    successful = 0
    failed = 0
    duplicates = 0
    
    for index, row in batch_df.iterrows():
        try:
            # Validate required fields
            sku = str(row.get('sku', '')).strip()
            name = str(row.get('name', '')).strip()
            
            if not sku or not name:
                validation_errors.append(f"Row {index + 1}: SKU and name are required")
                failed += 1
                continue
            
            # Check for existing product (case-insensitive SKU)
            existing_product = db.query(Product).filter(
                func.lower(Product.sku) == sku.lower()
            ).first()
            
            # Prepare product data
            product_data = {
                'sku': sku,
                'name': name,
                'description': str(row.get('description', '')).strip() or None,
                'price': parse_float(row.get('price')),
                'category': str(row.get('category', '')).strip() or None,
                'brand': str(row.get('brand', '')).strip() or None,
                'inventory_count': parse_int(row.get('inventory_count', 0)),
                'is_active': parse_bool(row.get('is_active', True))
            }
            
            if existing_product:
                # Update existing product
                for key, value in product_data.items():
                    if value is not None:
                        setattr(existing_product, key, value)
                existing_product.updated_at = datetime.utcnow()
                duplicates += 1
            else:
                # Create new product
                product = Product(**product_data)
                db.add(product)
            
            successful += 1
            
        except Exception as e:
            validation_errors.append(f"Row {index + 1}: {str(e)}")
            failed += 1
    
    # Commit the batch
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        # If batch commit fails, try individual commits
        for index, row in batch_df.iterrows():
            try:
                # Re-process individual row with individual commit
                # This is a fallback for constraint violations
                process_single_product(db, row, index, validation_errors)
            except Exception:
                failed += 1
                successful = max(0, successful - 1)
    
    return {
        'successful': successful,
        'failed': failed,
        'duplicates': duplicates
    }


def process_single_product(db: Session, row: pd.Series, index: int, validation_errors: List[str]):
    """Process a single product with individual transaction."""
    sku = str(row.get('sku', '')).strip()
    name = str(row.get('name', '')).strip()
    
    if not sku or not name:
        validation_errors.append(f"Row {index + 1}: SKU and name are required")
        return
    
    existing_product = db.query(Product).filter(
        func.lower(Product.sku) == sku.lower()
    ).first()
    
    product_data = {
        'sku': sku,
        'name': name,
        'description': str(row.get('description', '')).strip() or None,
        'price': parse_float(row.get('price')),
        'category': str(row.get('category', '')).strip() or None,
        'brand': str(row.get('brand', '')).strip() or None,
        'inventory_count': parse_int(row.get('inventory_count', 0)),
        'is_active': parse_bool(row.get('is_active', True))
    }
    
    if existing_product:
        for key, value in product_data.items():
            if value is not None:
                setattr(existing_product, key, value)
        existing_product.updated_at = datetime.utcnow()
    else:
        product = Product(**product_data)
        db.add(product)
    
    db.commit()


def parse_float(value) -> float:
    """Safely parse float value."""
    if pd.isna(value) or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_int(value) -> int:
    """Safely parse integer value."""
    if pd.isna(value) or value == '':
        return 0
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def parse_bool(value) -> bool:
    """Safely parse boolean value."""
    if pd.isna(value):
        return True
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'active', 'enabled')
    try:
        return bool(int(value))
    except (ValueError, TypeError):
        return True