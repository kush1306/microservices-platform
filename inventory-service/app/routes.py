"""HTTP route handlers for the inventory microservice."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import (
    HealthResponse,
    InventoryCreate,
    InventoryListResponse,
    InventoryResponse,
    InventoryUpdate,
    MessageResponse,
    StockAdjustRequest,
)
from app.services import InventoryService

settings = get_settings()

router = APIRouter()


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """Provide an InventoryService bound to the request DB session."""
    return InventoryService(db)


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
    "/inventory",
    response_model=InventoryListResponse,
    tags=["Inventory"],
    summary="List inventory",
)
def list_inventory(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryListResponse:
    """Return a paginated list of inventory records."""
    items, total = service.list_inventory(skip=skip, limit=limit)
    return InventoryListResponse(total=total, items=items)


@router.get(
    "/inventory/product/{product_id}",
    response_model=InventoryListResponse,
    tags=["Inventory"],
    summary="List inventory by product id",
)
def list_inventory_by_product(
    product_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryListResponse:
    """Return inventory records for a given product."""
    items, total = service.list_by_product(product_id=product_id, skip=skip, limit=limit)
    return InventoryListResponse(total=total, items=items)


@router.get(
    "/inventory/{inventory_id}",
    response_model=InventoryResponse,
    tags=["Inventory"],
    summary="Get inventory by id",
)
def get_inventory(
    inventory_id: int,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Return a single inventory record by primary key."""
    return service.get_inventory(inventory_id)


@router.post(
    "/inventory",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Inventory"],
    summary="Create inventory",
)
def create_inventory(
    payload: InventoryCreate,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Create a new inventory record."""
    return service.create_inventory(payload)


@router.put(
    "/inventory/{inventory_id}",
    response_model=InventoryResponse,
    tags=["Inventory"],
    summary="Update inventory",
)
def update_inventory(
    inventory_id: int,
    payload: InventoryUpdate,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Fully update an existing inventory record."""
    return service.update_inventory(inventory_id, payload)


@router.delete(
    "/inventory/{inventory_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    tags=["Inventory"],
    summary="Delete inventory",
)
def delete_inventory(
    inventory_id: int,
    service: InventoryService = Depends(get_inventory_service),
) -> MessageResponse:
    """Delete an inventory record by primary key."""
    service.delete_inventory(inventory_id)
    return MessageResponse(message=f"Inventory {inventory_id} deleted successfully")


@router.patch(
    "/inventory/{inventory_id}/increase",
    response_model=InventoryResponse,
    tags=["Inventory"],
    summary="Increase stock quantity",
)
def increase_stock(
    inventory_id: int,
    payload: StockAdjustRequest,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Increase the total stock quantity."""
    return service.increase_stock(inventory_id, payload)


@router.patch(
    "/inventory/{inventory_id}/decrease",
    response_model=InventoryResponse,
    tags=["Inventory"],
    summary="Decrease stock quantity",
)
def decrease_stock(
    inventory_id: int,
    payload: StockAdjustRequest,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Decrease the total stock quantity."""
    return service.decrease_stock(inventory_id, payload)


@router.patch(
    "/inventory/{inventory_id}/reserve",
    response_model=InventoryResponse,
    tags=["Inventory"],
    summary="Reserve stock",
)
def reserve_stock(
    inventory_id: int,
    payload: StockAdjustRequest,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Reserve available stock."""
    return service.reserve_stock(inventory_id, payload)


@router.patch(
    "/inventory/{inventory_id}/release",
    response_model=InventoryResponse,
    tags=["Inventory"],
    summary="Release reserved stock",
)
def release_stock(
    inventory_id: int,
    payload: StockAdjustRequest,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Release previously reserved stock."""
    return service.release_stock(inventory_id, payload)
