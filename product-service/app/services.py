"""Business logic layer for product operations."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Product
from app.schemas import ProductCreate, ProductUpdate
from app.utils import get_logger, normalize_category, normalize_sku

logger = get_logger(__name__)


class ProductService:
    """Service encapsulating product CRUD and query business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_products(self, skip: int = 0, limit: int = 100) -> tuple[list[Product], int]:
        """Return a page of products and the total count."""
        query = self.db.query(Product)
        total = query.count()
        items = query.order_by(Product.id.asc()).offset(skip).limit(limit).all()
        logger.info("Listed products skip=%s limit=%s total=%s", skip, limit, total)
        return items, total

    def get_product(self, product_id: int) -> Product:
        """Fetch a product by id or raise 404."""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            logger.warning("Product not found id=%s", product_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )
        return product

    def get_by_sku(self, sku: str) -> Product | None:
        """Fetch a product by normalized SKU."""
        return self.db.query(Product).filter(Product.sku == normalize_sku(sku)).first()

    def search_by_name(
        self,
        name: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Product], int]:
        """Search products by name (case-insensitive partial match)."""
        pattern = f"%{name.strip()}%"
        query = self.db.query(Product).filter(Product.name.ilike(pattern))
        total = query.count()
        items = query.order_by(Product.name.asc()).offset(skip).limit(limit).all()
        logger.info("Searched products name=%r skip=%s limit=%s total=%s", name, skip, limit, total)
        return items, total

    def list_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Product], int]:
        """List products belonging to a category (case-insensitive exact match)."""
        normalized = normalize_category(category)
        query = self.db.query(Product).filter(Product.category.ilike(normalized))
        total = query.count()
        items = query.order_by(Product.id.asc()).offset(skip).limit(limit).all()
        logger.info(
            "Listed products by category=%r skip=%s limit=%s total=%s",
            category,
            skip,
            limit,
            total,
        )
        return items, total

    def create_product(self, payload: ProductCreate) -> Product:
        """Create a new product after SKU uniqueness checks."""
        sku = normalize_sku(payload.sku)
        category = normalize_category(payload.category)

        if self.get_by_sku(sku) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU is already in use",
            )

        product = Product(
            name=payload.name.strip(),
            description=payload.description.strip(),
            category=category,
            price=payload.price,
            quantity=payload.quantity,
            sku=sku,
            image_url=str(payload.image_url) if payload.image_url is not None else None,
        )
        self.db.add(product)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error while creating product sku=%s", sku)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product with the same SKU already exists",
            ) from exc

        self.db.refresh(product)
        logger.info("Created product id=%s sku=%s", product.id, product.sku)
        return product

    def update_product(self, product_id: int, payload: ProductUpdate) -> Product:
        """Replace an existing product's fields."""
        product = self.get_product(product_id)
        sku = normalize_sku(payload.sku)
        category = normalize_category(payload.category)

        existing_sku = self.get_by_sku(sku)
        if existing_sku is not None and existing_sku.id != product.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU is already in use",
            )

        product.name = payload.name.strip()
        product.description = payload.description.strip()
        product.category = category
        product.price = payload.price
        product.quantity = payload.quantity
        product.sku = sku
        product.image_url = str(payload.image_url) if payload.image_url is not None else None

        self.db.add(product)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error while updating product id=%s", product_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product with the same SKU already exists",
            ) from exc

        self.db.refresh(product)
        logger.info("Updated product id=%s", product.id)
        return product

    def delete_product(self, product_id: int) -> None:
        """Delete a product by id."""
        product = self.get_product(product_id)
        self.db.delete(product)
        self.db.commit()
        logger.info("Deleted product id=%s", product_id)
