from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...models import Webhook
from ...schemas import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookTestRequest,
    WebhookTestResponse
)
from ...tasks.webhook_tasks import test_webhook_task


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    webhook: WebhookCreate,
    db: Session = Depends(get_db)
):
    """Create a new webhook."""
    
    # Convert Pydantic model to dict and handle URL conversion
    webhook_data = webhook.model_dump()
    webhook_data['url'] = str(webhook_data['url'])  # Convert HttpUrl to string
    
    db_webhook = Webhook(**webhook_data)
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    
    return db_webhook


@router.get("/", response_model=List[WebhookResponse])
def get_webhooks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all webhooks."""
    
    webhooks = db.query(Webhook).offset(skip).limit(limit).all()
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific webhook."""
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return webhook


@router.put("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: int,
    webhook_update: WebhookUpdate,
    db: Session = Depends(get_db)
):
    """Update a webhook."""
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Update fields
    update_data = webhook_update.model_dump(exclude_unset=True)
    # Convert HttpUrl to string if present
    if 'url' in update_data and update_data['url'] is not None:
        update_data['url'] = str(update_data['url'])
    
    for field, value in update_data.items():
        setattr(webhook, field, value)
    
    db.commit()
    db.refresh(webhook)
    
    return webhook


@router.delete("/{webhook_id}")
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db)
):
    """Delete a webhook."""
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    db.delete(webhook)
    db.commit()
    
    return {"message": "Webhook deleted successfully"}


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
def test_webhook(
    webhook_id: int,
    test_request: WebhookTestRequest,
    db: Session = Depends(get_db)
):
    """Test a webhook endpoint."""
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Check if webhook handles this event type
    if test_request.event_type not in webhook.event_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook doesn't handle event type: {test_request.event_type}"
        )
    
    # Start test task
    task = test_webhook_task.delay(
        webhook_id,
        test_request.event_type,
        test_request.test_data
    )
    
    # Wait for result (synchronous for testing)
    try:
        result = task.get(timeout=30)  # 30 second timeout for test
        return WebhookTestResponse(
            success=result.get('success', False),
            response_code=result.get('response_code'),
            response_time_ms=result.get('response_time_ms'),
            response_body=result.get('response_body'),
            error_message=result.get('error')
        )
    except Exception as e:
        return WebhookTestResponse(
            success=False,
            error_message=str(e)
        )


@router.get("/{webhook_id}/logs")
def get_webhook_logs(
    webhook_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get webhook execution logs."""
    
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    from ...models import WebhookLog
    
    logs = db.query(WebhookLog).filter(
        WebhookLog.webhook_id == webhook_id
    ).order_by(
        WebhookLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return logs