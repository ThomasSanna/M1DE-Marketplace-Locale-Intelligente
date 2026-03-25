from datetime import datetime
from decimal import Decimal
from uuid import UUID

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

@router.post("/payments")
def simulate_payment():
    """Simulateur de Paiement. Valide la commande et prélève les stocks définitivement."""
    return {"message": "Payment simulated"}

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
