from fastapi import APIRouter
from .import_routes import router as import_router
from .product_routes import router as product_router
from .webhook_routes import router as webhook_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(import_router)
api_router.include_router(product_router)
api_router.include_router(webhook_router)