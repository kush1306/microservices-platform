"""Business logic layer for inventory operations."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Inventory
from app.schemas import InventoryCreate, InventoryUpdate, StockAdjustRequest
from app.utils import available_quantity, get_logger, normalize_sku, normalize_warehouse

logger = get_logger(__name__)


class InventoryService:
    """Service encapsulating inventory CRUD and stock adjustment logic."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_inventory(self, skip: int = 0, limit: int = 100) -> tuple[list[Inventory], int]:
        """Return a page of inventory records and the total count."""
        query = self.db.query(Inventory)
        total = query.count()
        items = query.order_by(Inventory.id.asc()).offset(skip).limit(limit).all()
        logger.info("Listed inventory skip=%s limit=%s total=%s", skip, limit, total)
        return items, total

    def get_inventory(self, inventory_id: int) -> Inventory:
        """Fetch an inventory record by id or raise 404."""
        inventory = self.db.query(Inventory).filter(Inventory.id == inventory_id).first()
        if inventory is None:
            logger.warning("Inventory not found id=%s", inventory_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory with id {inventory_id} not found",
            )
        return inventory

    def get_by_sku(self, sku: str) -> Inventory | None:
        """Fetch an inventory record by normalized SKU."""
        return self.db.query(Inventory).filter(Inventory.sku == normalize_sku(sku)).first()

    def list_by_product(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Inventory], int]:
        """List inventory records for a given product id."""
        query = self.db.query(Inventory).filter(Inventory.product_id == product_id)
        total = query.count()
        items = query.order_by(Inventory.id.asc()).offset(skip).limit(limit).all()
        logger.info(
            "Listed inventory by product_id=%s skip=%s limit=%s total=%s",
            product_id,
            skip,
            limit,
            total,
        )
        return items, total

    def create_inventory(self, payload: InventoryCreate) -> Inventory:
        """Create a new inventory record after SKU uniqueness checks."""
        sku = normalize_sku(payload.sku)
        warehouse = normalize_warehouse(payload.warehouse)

        if self.get_by_sku(sku) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU is already in use",
            )

        inventory = Inventory(
            product_id=payload.product_id,
            sku=sku,
            quantity=payload.quantity,
            reserved_quantity=payload.reserved_quantity,
            warehouse=warehouse,
            low_stock_threshold=payload.low_stock_threshold,
        )
        self.db.add(inventory)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error while creating inventory sku=%s", sku)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Inventory with the same SKU already exists",
            ) from exc

        self.db.refresh(inventory)
        logger.info("Created inventory id=%s sku=%s", inventory.id, inventory.sku)
        return inventory

    def update_inventory(self, inventory_id: int, payload: InventoryUpdate) -> Inventory:
        """Replace an existing inventory record's fields."""
        inventory = self.get_inventory(inventory_id)
        sku = normalize_sku(payload.sku)
        warehouse = normalize_warehouse(payload.warehouse)

        existing_sku = self.get_by_sku(sku)
        if existing_sku is not None and existing_sku.id != inventory.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU is already in use",
            )

        inventory.product_id = payload.product_id
        inventory.sku = sku
        inventory.quantity = payload.quantity
        inventory.reserved_quantity = payload.reserved_quantity
        inventory.warehouse = warehouse
        inventory.low_stock_threshold = payload.low_stock_threshold

        self.db.add(inventory)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error while updating inventory id=%s", inventory_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Inventory with the same SKU already exists",
            ) from exc

        self.db.refresh(inventory)
        logger.info("Updated inventory id=%s", inventory.id)
        return inventory

    def delete_inventory(self, inventory_id: int) -> None:
        """Delete an inventory record by id."""
        inventory = self.get_inventory(inventory_id)
        self.db.delete(inventory)
        self.db.commit()
        logger.info("Deleted inventory id=%s", inventory_id)

    def increase_stock(self, inventory_id: int, payload: StockAdjustRequest) -> Inventory:
        """Increase the total quantity of an inventory record."""
        inventory = self.get_inventory(inventory_id)
        inventory.quantity += payload.amount
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        logger.info(
            "Increased inventory id=%s by amount=%s new_quantity=%s",
            inventory_id,
            payload.amount,
            inventory.quantity,
        )
        return inventory

    def decrease_stock(self, inventory_id: int, payload: StockAdjustRequest) -> Inventory:
        """Decrease the total quantity without going below reserved stock."""
        inventory = self.get_inventory(inventory_id)
        if payload.amount > available_quantity(inventory.quantity, inventory.reserved_quantity):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Cannot decrease by more than available stock "
                    f"({available_quantity(inventory.quantity, inventory.reserved_quantity)})"
                ),
            )
        inventory.quantity -= payload.amount
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        logger.info(
            "Decreased inventory id=%s by amount=%s new_quantity=%s",
            inventory_id,
            payload.amount,
            inventory.quantity,
        )
        return inventory

    def reserve_stock(self, inventory_id: int, payload: StockAdjustRequest) -> Inventory:
        """Reserve available stock for an order."""
        inventory = self.get_inventory(inventory_id)
        available = available_quantity(inventory.quantity, inventory.reserved_quantity)
        if payload.amount > available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reserve more than available stock ({available})",
            )
        inventory.reserved_quantity += payload.amount
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        logger.info(
            "Reserved inventory id=%s amount=%s reserved_quantity=%s",
            inventory_id,
            payload.amount,
            inventory.reserved_quantity,
        )
        return inventory

    def release_stock(self, inventory_id: int, payload: StockAdjustRequest) -> Inventory:
        """Release previously reserved stock."""
        inventory = self.get_inventory(inventory_id)
        if payload.amount > inventory.reserved_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Cannot release more than reserved quantity "
                    f"({inventory.reserved_quantity})"
                ),
            )
        inventory.reserved_quantity -= payload.amount
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        logger.info(
            "Released inventory id=%s amount=%s reserved_quantity=%s",
            inventory_id,
            payload.amount,
            inventory.reserved_quantity,
        )
        return inventory
