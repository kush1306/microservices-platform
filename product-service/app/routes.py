"""HTTP route handlers for the product microservice."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import (
    HealthResponse,
    MessageResponse,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services import ProductService

settings = get_settings()

router = APIRouter()


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Provide a ProductService bound to the request DB session."""
    return ProductService(db)


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
)
def health_check() -> HealthResponse:
    """Return service health information."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get(
    "/products",
    response_model=ProductListResponse,
    tags=["Products"],
    summary="List products",
)
def list_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: ProductService = Depends(get_product_service),
) -> ProductListResponse:
    """Return a paginated list of products."""
    items, total = service.list_products(skip=skip, limit=limit)
    return ProductListResponse(total=total, items=items)


@router.get(
    "/products/search",
    response_model=ProductListResponse,
    tags=["Products"],
    summary="Search products by name",
)
def search_products(
    name: str = Query(..., min_length=1, description="Product name search term"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: ProductService = Depends(get_product_service),
) -> ProductListResponse:
    """Search products by name (case-insensitive partial match)."""
    items, total = service.search_by_name(name=name, skip=skip, limit=limit)
    return ProductListResponse(total=total, items=items)


@router.get(
    "/products/category/{category}",
    response_model=ProductListResponse,
    tags=["Products"],
    summary="List products by category",
)
def list_products_by_category(
    category: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: ProductService = Depends(get_product_service),
) -> ProductListResponse:
    """Return products in the given category."""
    items, total = service.list_by_category(category=category, skip=skip, limit=limit)
    return ProductListResponse(total=total, items=items)


@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Get product by id",
)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Return a single product by primary key."""
    return service.get_product(product_id)


@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Create product",
)
def create_product(
    payload: ProductCreate,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Create a new product."""
    return service.create_product(payload)


@router.put(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Update product",
)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Fully update an existing product."""
    return service.update_product(product_id, payload)


@router.delete(
    "/products/{product_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    tags=["Products"],
    summary="Delete product",
)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
) -> MessageResponse:
    """Delete a product by primary key."""
    service.delete_product(product_id)
    return MessageResponse(message=f"Product {product_id} deleted successfully")
