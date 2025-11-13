#!/usr/bin/env python3
"""
Initialize the database for local development
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import Product, Webhook, WebhookLog, ImportJob

def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    print("🎯 You can now start the application")

if __name__ == "__main__":
    init_db()