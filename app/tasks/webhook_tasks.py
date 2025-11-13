from celery import current_task
from sqlalchemy.orm import Session
import httpx
import time
import json
from typing import Dict, Any, List
from datetime import datetime

from ..celery import celery_app
from ..database import SessionLocal
from ..models import Webhook, WebhookLog


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, queue='webhook_queue')
def send_webhook_task(self, webhook_id: int, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send webhook notification for an event.
    """
    db = SessionLocal()
    
    try:
        # Get webhook configuration
        webhook = db.query(Webhook).filter(
            Webhook.id == webhook_id,
            Webhook.is_active == True
        ).first()
        
        if not webhook:
            return {"success": False, "error": "Webhook not found or inactive"}
        
        # Check if webhook handles this event type
        if event_type not in webhook.event_types:
            return {"success": False, "error": f"Webhook doesn't handle event type: {event_type}"}
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ProductImporter-Webhook/1.0"
        }
        
        # Add custom headers
        if webhook.headers:
            headers.update(webhook.headers)
        
        # Add signature if secret key is provided
        if webhook.secret_key:
            signature = generate_signature(payload, webhook.secret_key)
            headers["X-Webhook-Signature"] = signature
        
        # Send webhook
        start_time = time.time()
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    str(webhook.url),
                    json=payload,
                    headers=headers,
                    timeout=webhook.timeout_seconds
                )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            success = 200 <= response.status_code < 300
            
            # Log webhook call
            webhook_log = WebhookLog(
                webhook_id=webhook_id,
                event_type=event_type,
                payload=payload,
                response_code=response.status_code,
                response_body=response.text[:1000],  # Limit response body size
                response_time_ms=response_time_ms,
                success=success,
                retry_attempt=self.request.retries
            )
            db.add(webhook_log)
            
            # Update webhook stats
            webhook.last_triggered_at = datetime.utcnow()
            webhook.last_response_code = response.status_code
            webhook.last_response_time_ms = response_time_ms
            
            db.commit()
            
            if not success:
                # Retry if not successful
                if self.request.retries < self.max_retries:
                    self.retry(countdown=60 * (self.request.retries + 1))
                return {
                    "success": False,
                    "response_code": response.status_code,
                    "response_body": response.text,
                    "response_time_ms": response_time_ms
                }
            
            return {
                "success": True,
                "response_code": response.status_code,
                "response_time_ms": response_time_ms
            }
            
        except httpx.TimeoutException:
            # Log timeout error
            webhook_log = WebhookLog(
                webhook_id=webhook_id,
                event_type=event_type,
                payload=payload,
                error_message="Request timeout",
                success=False,
                retry_attempt=self.request.retries
            )
            db.add(webhook_log)
            db.commit()
            
            if self.request.retries < self.max_retries:
                self.retry(countdown=60 * (self.request.retries + 1))
            
            return {"success": False, "error": "Request timeout"}
            
        except Exception as e:
            # Log other errors
            webhook_log = WebhookLog(
                webhook_id=webhook_id,
                event_type=event_type,
                payload=payload,
                error_message=str(e),
                success=False,
                retry_attempt=self.request.retries
            )
            db.add(webhook_log)
            db.commit()
            
            if self.request.retries < self.max_retries:
                self.retry(countdown=60 * (self.request.retries + 1))
            
            return {"success": False, "error": str(e)}
    
    finally:
        db.close()


@celery_app.task(queue='webhook_queue')
def trigger_webhook_task(event_type: str, payload: Dict[str, Any]):
    """
    Trigger all active webhooks for a specific event type.
    """
    from sqlalchemy import text
    
    db = SessionLocal()
    
    try:
        # Get all active webhooks that handle this event type
        # Cast both JSON and parameter to JSONB for PostgreSQL @> operator
        webhooks = db.query(Webhook).filter(
            Webhook.is_active == True,
            text("CAST(event_types AS jsonb) @> CAST(:event_type AS jsonb)")
        ).params(event_type=f'["{event_type}"]').all()
        
        # Send webhook to each configured endpoint
        for webhook in webhooks:
            send_webhook_task.apply_async((webhook.id, event_type, payload), queue='webhook_queue')
        
        return {"triggered_webhooks": len(webhooks)}
    
    finally:
        db.close()


@celery_app.task(queue='webhook_queue')
def test_webhook_task(webhook_id: int, event_type: str, test_payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Test a webhook endpoint.
    """
    if test_payload is None:
        test_payload = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "test": True,
            "data": {
                "message": "This is a test webhook"
            }
        }
    
    return send_webhook_task(webhook_id, event_type, test_payload)


def generate_signature(payload: Dict[str, Any], secret_key: str) -> str:
    """
    Generate HMAC signature for webhook verification.
    """
    import hmac
    import hashlib
    
    payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
    signature = hmac.new(
        secret_key.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    return f"sha256={signature}"