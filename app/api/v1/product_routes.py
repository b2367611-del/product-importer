from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
import math
from datetime import datetime

from ...database import get_db
from ...models import Product
from ...schemas import (
    ProductCreate,
    ProductUpdate, 
    ProductResponse,
    ProductListResponse,
    ProductFilter
)
from ...tasks.webhook_tasks import trigger_webhook_task


router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product."""
    
    # Check if SKU already exists (case-insensitive)
    existing = db.query(Product).filter(
        func.lower(Product.sku) == product.sku.lower()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product.sku}' already exists"
        )
    
    # Create new product
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Trigger webhook
    trigger_webhook_task.delay(
        'product.created',
        {
            'id': db_product.id,
            'sku': db_product.sku,
            'name': db_product.name,
            'timestamp': db_product.created_at.isoformat()
        }
    )
    
    return db_product


@router.get("/", response_model=ProductListResponse)
def get_products(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    sku: Optional[str] = None,
    name: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    is_active: Optional[bool] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """Get products with filtering and pagination."""
    
    query = db.query(Product)
    
    # Apply filters
    if sku:
        query = query.filter(Product.sku.ilike(f"%{sku}%"))
    
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    products = query.order_by(Product.name).offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 1
    
    return ProductListResponse(
        items=products,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific product by ID."""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product."""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check SKU uniqueness if being updated
    if product_update.sku and product_update.sku.lower() != product.sku.lower():
        existing = db.query(Product).filter(
            func.lower(Product.sku) == product_update.sku.lower(),
            Product.id != product_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_update.sku}' already exists"
            )
    
    # Update fields
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    # Trigger webhook
    trigger_webhook_task.delay(
        'product.updated',
        {
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
            'timestamp': product.updated_at.isoformat()
        }
    )
    
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Delete a product."""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Store product data for webhook
    product_data = {
        'id': product.id,
        'sku': product.sku,
        'name': product.name,
        'timestamp': product.updated_at.isoformat()
    }
    
    db.delete(product)
    db.commit()
    
    # Trigger webhook
    trigger_webhook_task.delay('product.deleted', product_data)
    
    return {"message": "Product deleted successfully"}


@router.delete("/")
def delete_all_products(
    confirm: bool = Query(False, description="Confirm deletion of all products"),
    db: Session = Depends(get_db)
):
    """Delete all products (bulk delete)."""
    
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please confirm deletion by setting confirm=true"
        )
    
    # Get count before deletion
    total_count = db.query(Product).count()
    
    if total_count == 0:
        return {"message": "No products to delete", "deleted_count": 0}
    
    # Delete all products
    deleted_count = db.query(Product).delete()
    db.commit()
    
    # Trigger webhook
    trigger_webhook_task.delay(
        'products.bulk_deleted',
        {
            'deleted_count': deleted_count,
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    return {
        "message": f"Successfully deleted {deleted_count} products",
        "deleted_count": deleted_count
    }


@router.get("/search/suggestions")
def get_search_suggestions(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """Get search suggestions for products."""
    
    # Get SKU suggestions
    sku_suggestions = db.query(Product.sku).filter(
        Product.sku.ilike(f"%{q}%")
    ).limit(10).all()
    
    # Get name suggestions  
    name_suggestions = db.query(Product.name).filter(
        Product.name.ilike(f"%{q}%")
    ).limit(10).all()
    
    # Get category suggestions
    category_suggestions = db.query(Product.category).filter(
        Product.category.ilike(f"%{q}%"),
        Product.category.is_not(None)
    ).distinct().limit(10).all()
    
    # Get brand suggestions
    brand_suggestions = db.query(Product.brand).filter(
        Product.brand.ilike(f"%{q}%"),
        Product.brand.is_not(None)
    ).distinct().limit(10).all()
    
    return {
        "skus": [s[0] for s in sku_suggestions],
        "names": [n[0] for n in name_suggestions],
        "categories": [c[0] for c in category_suggestions],
        "brands": [b[0] for b in brand_suggestions]
    }