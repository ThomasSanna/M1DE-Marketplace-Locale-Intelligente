from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import crud, schemas, models
from database import get_db
from api.v1.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[schemas.ProductResponse])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Liste les produits de la marketplace (avec pagination et filtres géographiques/prix)."""
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Récupère les détails spécifiques d'un produit."""
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Auth Producer] Ajoute un nouveau produit au catalogue."""
    if current_user.role != models.UserRole.producer:
        raise HTTPException(status_code=403, detail="Only users with producer role can create products")
    
    producer = crud.get_producer_by_user_id(db, user_id=current_user.id)
    if not producer:
        raise HTTPException(status_code=400, detail="Producer profile not found for the user")

    return crud.create_product(db=db, product=product, producer_id=producer.id)

@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: UUID,
    product: schemas.ProductUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Auth Producer] Modifie un produit existant ou ajuste le stock."""
    if current_user.role != models.UserRole.producer:
        raise HTTPException(status_code=403, detail="Only users with producer role can update products")
    
    producer = crud.get_producer_by_user_id(db, user_id=current_user.id)
    if not producer:
        raise HTTPException(status_code=400, detail="Producer profile not found for the user")
        
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if db_product.producer_id != producer.id:
        raise HTTPException(status_code=403, detail="You can only update your own products")

    return crud.update_product(db=db, product_id=product_id, product=product)

@router.delete("/{product_id}", response_model=schemas.ProductResponse)
def delete_product(
    product_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Auth Producer] Supprime/Désactive un produit."""
    if current_user.role != models.UserRole.producer:
        raise HTTPException(status_code=403, detail="Only users with producer role can delete products")
        
    producer = crud.get_producer_by_user_id(db, user_id=current_user.id)
    if not producer:
        raise HTTPException(status_code=400, detail="Producer profile not found for the user")
        
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if db_product.producer_id != producer.id:
        raise HTTPException(status_code=403, detail="You can only delete your own products")

    return crud.delete_product(db=db, product_id=product_id)
