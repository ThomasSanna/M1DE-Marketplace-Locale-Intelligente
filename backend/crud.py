from sqlalchemy.orm import Session
from uuid import UUID
import models, schemas, auth_utils
from datetime import datetime

def get_user(db: Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth_utils.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_login(db: Session, user_id: UUID):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    return db_user

def create_producer(db: Session, producer: schemas.ProducerCreate, user_id: UUID):
    db_producer = models.Producer(**producer.dict(), user_id=user_id)
    db.add(db_producer)
    db.commit()
    db.refresh(db_producer)
    return db_producer

def get_producers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Producer).offset(skip).limit(limit).all()

def get_producer(db: Session, producer_id: UUID):
    return db.query(models.Producer).filter(models.Producer.id == producer_id).first()

def get_products_by_producer(db: Session, producer_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Product).filter(models.Product.producer_id == producer_id).offset(skip).limit(limit).all()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: UUID):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_producer_by_user_id(db: Session, user_id: UUID):
    return db.query(models.Producer).filter(models.Producer.user_id == user_id).first()

def create_product(db: Session, product: schemas.ProductCreate, producer_id: UUID):
    db_product = models.Product(**product.dict(), producer_id=producer_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: UUID, product: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db_product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: UUID):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product
