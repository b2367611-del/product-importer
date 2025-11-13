from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Float, Index
from sqlalchemy.sql import func
from ..database import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    brand = Column(String(100), nullable=True, index=True)
    inventory_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Create composite indexes for common queries
    __table_args__ = (
        Index('idx_products_sku_lower', func.lower(sku)),
        Index('idx_products_name_active', name, is_active),
        Index('idx_products_category_active', category, is_active),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"