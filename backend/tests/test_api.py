from datetime import datetime
from decimal import Decimal
from uuid import UUID
import random
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud, models, schemas
from api.v1.dependencies import get_current_user
from database import get_db

router = APIRouter(tags=["Orders & Payments"])

_ALLOWED_TRANSITIONS = {
    models.OrderStatus.draft: {models.OrderStatus.confirmed, models.OrderStatus.cancelled},
    models.OrderStatus.confirmed: {models.OrderStatus.shipped, models.OrderStatus.cancelled},
    models.OrderStatus.shipped: {models.OrderStatus.delivered},
    models.OrderStatus.delivered: set(),
    models.OrderStatus.cancelled: set(),
}

_SIMULATED_ERROR_RATE = 0.05
_IDEMPOTENCY_CACHE = {}

_CONTROLLED_ERROR_SCENARIOS = {
    "insufficient_funds": {
        "http_status": status.HTTP_402_PAYMENT_REQUIRED,
        "error_code": "INSUFFICIENT_FUNDS",
        "retryable": False,
        "message": "Paiement refuse: fonds insuffisants.",
    },
    "provider_timeout": {
        "http_status": status.HTTP_504_GATEWAY_TIMEOUT,
        "error_code": "PROVIDER_TIMEOUT",
        "retryable": True,
        "message": "Delai depasse du fournisseur de paiement.",
    },
    "fraud_suspected": {
        "http_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "error_code": "FRAUD_SUSPECTED",
        "retryable": False,
        "message": "Transaction bloquee pour suspicion de fraude.",
    },
    "network_error": {
        "http_status": status.HTTP_503_SERVICE_UNAVAILABLE,
        "error_code": "NETWORK_ERROR",
        "retryable": True,
        "message": "Erreur reseau temporaire vers le provider.",
    },
}


def _resolve_scenario(requested_scenario: str) -> str:
    if requested_scenario != "auto":
        return requested_scenario

    if random.random() < _SIMULATED_ERROR_RATE:
        return random.choice(list(_CONTROLLED_ERROR_SCENARIOS.keys()))

    return "success"


def _build_provider_reference() -> str:
    return f"SIM-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8].upper()}"


@router.post("/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: schemas.OrderCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Transforme le panier Front-end en Commande (Brouillon)."""
    if current_user.role != models.UserRole.client:
        raise HTTPException(status_code=403, detail="Only clients can create orders")

    aggregated_quantities = {}
    for item in payload.items:
        aggregated_quantities[item.product_id] = aggregated_quantities.get(item.product_id, Decimal("0")) + Decimal(str(item.quantity))

    total_amount = Decimal("0")
    order_items = []

    for product_id, quantity in aggregated_quantities.items():
        if quantity <= 0:
            raise HTTPException(status_code=422, detail=f"Invalid quantity for product {product_id}")

        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if db_product is None:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        if not db_product.is_active:
            raise HTTPException(status_code=409, detail=f"Product {product_id} is inactive")

        unit_price = Decimal(str(db_product.price))
        total_amount += unit_price * quantity

        order_items.append(
            models.OrderItem(
                product_id=product_id,
                quantity=quantity,
                unit_price_snapshot=unit_price,
            )
        )

    db_order = models.Order(
        client_id=current_user.id,
        status=models.OrderStatus.draft,
        total_amount=total_amount,
    )
    db.add(db_order)
    db.flush()

    for item in order_items:
        item.order_id = db_order.id
        item.order = db_order
        db.add(item)

    db.commit()
    db.refresh(db_order)

    return db_order