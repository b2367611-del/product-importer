from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class WebhookBase(BaseModel):
    name: str = Field(..., max_length=255, description="Webhook name")
    url: HttpUrl = Field(..., description="Webhook URL")
    event_types: List[str] = Field(..., description="List of event types to trigger on")
    is_active: bool = Field(True, description="Is webhook active")
    secret_key: Optional[str] = Field(None, max_length=255, description="Secret key for verification")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers")
    retry_count: int = Field(3, ge=0, le=10, description="Number of retries")
    timeout_seconds: int = Field(30, ge=1, le=300, description="Timeout in seconds")


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    url: Optional[HttpUrl] = None
    event_types: Optional[List[str]] = None
    is_active: Optional[bool] = None
    secret_key: Optional[str] = Field(None, max_length=255)
    headers: Optional[Dict[str, str]] = None
    retry_count: Optional[int] = Field(None, ge=0, le=10)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300)


class WebhookResponse(WebhookBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    last_triggered_at: Optional[datetime]
    last_response_code: Optional[int]
    last_response_time_ms: Optional[int]
    created_at: datetime
    updated_at: datetime


class WebhookTestRequest(BaseModel):
    event_type: str = Field(..., description="Event type to test")
    test_data: Optional[Dict[str, Any]] = Field(None, description="Test payload data")


class WebhookTestResponse(BaseModel):
    success: bool
    response_code: Optional[int]
    response_time_ms: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]