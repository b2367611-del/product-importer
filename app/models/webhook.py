from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON
from sqlalchemy.sql import func
from ..database import Base


class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    event_types = Column(JSON, nullable=False)  # List of event types: ['product.created', 'product.updated', etc.]
    is_active = Column(Boolean, default=True, nullable=False)
    secret_key = Column(String(255), nullable=True)  # For webhook verification
    headers = Column(JSON, nullable=True)  # Additional headers to send
    retry_count = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=30)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    last_response_code = Column(Integer, nullable=True)
    last_response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Webhook(id={self.id}, name='{self.name}', url='{self.url}')>"


class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    response_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_attempt = Column(Integer, default=0)
    success = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<WebhookLog(id={self.id}, webhook_id={self.webhook_id}, event='{self.event_type}')>"