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

@router.get("/orders", response_model=list[schemas.OrderResponse])
def list_orders(
    status_filter: models.OrderStatus | None = Query(default=None, alias="status"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[Auth] Récupération de l'historique des commandes d'un utilisateur."""
    query = db.query(models.Order).filter(models.Order.client_id == current_user.id)
    if status_filter is not None:
        query = query.filter(models.Order.status == status_filter)
    return query.order_by(models.Order.created_at.desc()).all()

@router.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: UUID, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Détail d'une commande."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.client_id != current_user.id and current_user.role != models.UserRole.producer:
        raise HTTPException(status_code=403, detail="Not allowed to access this order")

    return db_order

@router.post(
    "/payments",
    response_model=schemas.PaymentSimulationResponse,
    responses={
        402: {"model": schemas.PaymentErrorResponse},
        422: {"model": schemas.PaymentErrorResponse},
        503: {"model": schemas.PaymentErrorResponse},
        504: {"model": schemas.PaymentErrorResponse},
    },
)
def simulate_payment(
    payload: schemas.PaymentSimulationRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Simulateur de paiement avec erreurs controlees et comportement idempotent."""
    if current_user.role != models.UserRole.client:
        raise HTTPException(status_code=403, detail="Only clients can trigger payments")

    if payload.idempotency_key and payload.idempotency_key in _IDEMPOTENCY_CACHE:
        cached = _IDEMPOTENCY_CACHE[payload.idempotency_key]
        if cached["is_error"]:
            raise HTTPException(status_code=cached["http_status"], detail=cached["payload"])
        return schemas.PaymentSimulationResponse(**cached["payload"])

    db_order = db.query(models.Order).filter(models.Order.id == payload.order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only pay your own orders")

    if db_order.status in [models.OrderStatus.confirmed, models.OrderStatus.shipped, models.OrderStatus.delivered]:
        raise HTTPException(status_code=409, detail="Order already paid or already in fulfillment")

    if db_order.status == models.OrderStatus.cancelled:
        raise HTTPException(status_code=409, detail="Cancelled orders cannot be paid")

    amount = float(db_order.total_amount)
    if amount <= 0:
        raise HTTPException(status_code=422, detail="Order total amount must be greater than zero")

    order_items = list(db_order.items or [])
    if not order_items:
        raise HTTPException(status_code=422, detail="Order has no items")

    if payload.processing_delay_ms > 0:
        time.sleep(payload.processing_delay_ms / 1000)

    db_payment = db.query(models.Payment).filter(models.Payment.order_id == payload.order_id).first()
    scenario = _resolve_scenario(payload.simulate_scenario)
    provider_reference = _build_provider_reference()

    if scenario == "success":
        # Stock debit is applied only when payment succeeds.
        for item in order_items:
            product = item.product
            if product is None:
                product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if product is None:
                raise HTTPException(status_code=404, detail=f"Product not found for order item {item.id}")
            if not product.is_active:
                raise HTTPException(status_code=409, detail=f"Product {product.id} is inactive")

            available_stock = Decimal(str(product.stock_quantity))
            requested_qty = Decimal(str(item.quantity))
            if requested_qty <= 0:
                raise HTTPException(status_code=422, detail=f"Invalid quantity for order item {item.id}")
            if available_stock < requested_qty:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "INSUFFICIENT_STOCK",
                        "message": f"Stock insuffisant pour le produit {product.id}.",
                        "available": float(available_stock),
                        "requested": float(requested_qty),
                    },
                )

            product.stock_quantity = available_stock - requested_qty
            product.updated_at = datetime.utcnow()

        if db_payment is None:
            db_payment = models.Payment(
                id=uuid.uuid4(),
                order_id=db_order.id,
                amount=amount,
                status=models.PaymentStatus.success,
                is_simulated_error=False,
            )
            db.add(db_payment)
        else:
            db_payment.amount = amount
            db_payment.status = models.PaymentStatus.success
            db_payment.is_simulated_error = False

        db_order.status = models.OrderStatus.confirmed
        db_order.confirmed_at = datetime.utcnow()
        db_order.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_payment)
        db.refresh(db_order)

        if db_payment.id is None:
            db_payment.id = uuid.uuid4()

        response_payload = {
            "payment_id": db_payment.id,
            "order_id": db_order.id,
            "status": db_payment.status,
            "order_status": db_order.status,
            "amount": float(db_payment.amount),
            "idempotency_key": payload.idempotency_key,
            "simulated_latency_ms": payload.processing_delay_ms,
            "retryable": False,
            "provider_reference": provider_reference,
        }

        if payload.idempotency_key:
            _IDEMPOTENCY_CACHE[payload.idempotency_key] = {
                "is_error": False,
                "http_status": status.HTTP_200_OK,
                "payload": response_payload,
            }

        return schemas.PaymentSimulationResponse(**response_payload)

    scenario_details = _CONTROLLED_ERROR_SCENARIOS[scenario]

    if db_payment is None:
        db_payment = models.Payment(
            id=uuid.uuid4(),
            order_id=db_order.id,
            amount=amount,
            status=models.PaymentStatus.failed,
            is_simulated_error=True,
        )
        db.add(db_payment)
    else:
        db_payment.amount = amount
        db_payment.status = models.PaymentStatus.failed
        db_payment.is_simulated_error = True

    db.commit()

    error_payload = {
        "error_code": scenario_details["error_code"],
        "message": scenario_details["message"],
        "retryable": scenario_details["retryable"],
        "order_id": str(db_order.id),
        "provider_reference": provider_reference,
    }

    if payload.idempotency_key:
        _IDEMPOTENCY_CACHE[payload.idempotency_key] = {
            "is_error": True,
            "http_status": scenario_details["http_status"],
            "payload": error_payload,
        }

    raise HTTPException(status_code=scenario_details["http_status"], detail=error_payload)

@router.patch("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: UUID,
    payload: schemas.OrderStatusUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Met à jour le cycle de vie de la commande avec des transitions métier contrôlées."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    target_status = payload.status

    if target_status == models.OrderStatus.cancelled:
        if db_order.client_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the order owner can cancel it")
    elif target_status in {models.OrderStatus.shipped, models.OrderStatus.delivered}:
        if current_user.role != models.UserRole.producer:
            raise HTTPException(status_code=403, detail="Only producers can set shipped or delivered status")

        producer = crud.get_producer_by_user_id(db, user_id=current_user.id)
        if producer is None:
            raise HTTPException(status_code=400, detail="Producer profile not found")

        order_products = db.query(models.Product).filter(models.Product.id.in_([item.product_id for item in db_order.items])).all()
        if not order_products or any(product.producer_id != producer.id for product in order_products):
            raise HTTPException(status_code=403, detail="You can only update orders for your own products")
    else:
        raise HTTPException(status_code=403, detail="Status transition not allowed for this actor")

    if target_status not in _ALLOWED_TRANSITIONS[db_order.status]:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid transition from {db_order.status.value} to {target_status.value}",
        )

    db_order.status = target_status
    db_order.updated_at = datetime.utcnow()
    if target_status == models.OrderStatus.confirmed:
        db_order.confirmed_at = datetime.utcnow()
    if target_status == models.OrderStatus.delivered:
        db_order.delivered_at = datetime.utcnow()

    db.commit()
    db.refresh(db_order)

    return db_order
