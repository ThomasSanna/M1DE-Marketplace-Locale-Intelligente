from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import crud, schemas, models
from database import get_db
from api.v1.dependencies import get_current_user

router = APIRouter(tags=["Orders & Payments"])


@router.post("/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: schemas.OrderCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Transforme le panier Front-end en Commande (Brouillon)."""
    try:
        return crud.create_order(db, order, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/orders", response_model=List[schemas.OrderResponse])
def list_orders(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[Auth] Récupération de l'historique des commandes d'un utilisateur."""
    return crud.get_orders_by_user(db, current_user.id)


@router.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Détail d'une commande."""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    if order.client_id != current_user.id and current_user.role != models.UserRole.producer:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    return order


@router.post("/payments", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED)
def simulate_payment(
    payload: schemas.PaymentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Simulateur de Paiement. Valide la commande et déduit les stocks."""
    order = crud.get_order(db, payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    if order.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    if order.status != models.OrderStatus.draft:
        raise HTTPException(status_code=400, detail="Cette commande a déjà été traitée")

    payment = crud.process_payment(db, payload.order_id)
    return payment


@router.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: UUID,
    body: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[Auth Producer] Mise à jour du statut d'expédition."""
    if current_user.role != models.UserRole.producer:
        raise HTTPException(status_code=403, detail="Réservé aux producteurs")
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    new_status = body.get("status")
    try:
        order.status = models.OrderStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Statut invalide : {new_status}")
    db.commit()
    db.refresh(order)
    return {"order_id": str(order.id), "status": order.status}
