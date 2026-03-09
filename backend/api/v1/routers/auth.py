from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import crud, schemas, auth_utils, models
from database import get_db
from api.v1.dependencies import get_current_user

router = APIRouter(tags=["Auth & Producers"])

@router.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouveau client ou producteur."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)

@router.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authentification (Retourne un JWT Token)."""
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not auth_utils.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Update last login at
    crud.update_user_login(db, user.id)

    access_token = auth_utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.UserResponse)
def get_user_profile(current_user: models.User = Depends(get_current_user)):
    """Récupération du profil. (Authentification requise)"""
    return current_user

@router.post("/producers", response_model=schemas.ProducerResponse, status_code=status.HTTP_201_CREATED)
def create_producer_profile(
    producer: schemas.ProducerCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un profil de producteur. L'utilisateur doit avoir le rôle 'producer'."""
    if current_user.role != models.UserRole.producer:
        raise HTTPException(status_code=403, detail="Only users with producer role can create a producer profile")
    
    db_producer = crud.get_producer(db, producer_id=current_user.id) # Wait, producer user_id is the relationship
    # Let's check if the current user already has a producer profile
    existing_producer = db.query(models.Producer).filter(models.Producer.user_id == current_user.id).first()
    if existing_producer:
         raise HTTPException(status_code=400, detail="User already has a producer profile")

    return crud.create_producer(db=db, producer=producer, user_id=current_user.id)

@router.get("/producers", response_model=List[schemas.ProducerResponse])
def list_producers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Liste tous les producteurs locaux."""
    producers = crud.get_producers(db, skip=skip, limit=limit)
    return producers

@router.get("/producers/{producer_id}/products", response_model=List[schemas.ProductResponse])
def get_producer_products(producer_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la vitrine/boutique d'un producteur spécifique."""
    producer = crud.get_producer(db, producer_id=producer_id)
    if not producer:
        raise HTTPException(status_code=404, detail="Producer not found")
    
    products = crud.get_products_by_producer(db, producer_id=producer_id, skip=skip, limit=limit)
    return products
