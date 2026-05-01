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


# ---- Order CRUD ---- #

def create_order(db: Session, order: schemas.OrderCreate, client_id: UUID):
    """Creates a draft order from cart items. Validates stock availability."""
    # Validate all products and stock first
    for item in order.items:
        product = get_product(db, item.product_id)
        if not product:
            raise ValueError(f"Produit introuvable : {item.product_id}")
        if not product.is_active:
            raise ValueError(f"Le produit '{product.name}' n'est plus disponible")
        if float(product.stock_quantity) < item.quantity:
            raise ValueError(f"Stock insuffisant pour '{product.name}' (disponible : {product.stock_quantity} {product.unit})")

    db_order = models.Order(client_id=client_id, total_amount=0)
    db.add(db_order)
    db.flush()

    total = 0.0
    for item in order.items:
        product = get_product(db, item.product_id)
        unit_price = float(product.price)
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price_snapshot=unit_price,
        )
        db.add(db_item)
        total += unit_price * item.quantity

    db_order.total_amount = round(total, 2)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_orders_by_user(db: Session, client_id: UUID):
    return (
        db.query(models.Order)
        .filter(models.Order.client_id == client_id)
        .order_by(models.Order.created_at.desc())
        .all()
    )


def get_order(db: Session, order_id: UUID):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def process_payment(db: Session, order_id: UUID):
    """Simulates payment: confirms order, deducts stock, creates Payment record."""
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    # Create payment record
    db_payment = models.Payment(
        order_id=order_id,
        amount=db_order.total_amount,
        status=models.PaymentStatus.success,
    )
    db.add(db_payment)

    # Confirm order
    db_order.status = models.OrderStatus.confirmed
    db_order.confirmed_at = datetime.utcnow()

    # Deduct stock
    for item in db_order.items:
        product = get_product(db, item.product_id)
        if product:
            product.stock_quantity = float(product.stock_quantity) - float(item.quantity)

    db.commit()
    db.refresh(db_payment)
    return db_payment
