import enum
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

# --- Enums ---
class UserRole(str, enum.Enum):
    client = 'client'
    producer = 'producer'

class OrderStatus(str, enum.Enum):
    draft = 'draft'
    confirmed = 'confirmed'
    shipped = 'shipped'
    delivered = 'delivered'
    cancelled = 'cancelled'

class PaymentStatus(str, enum.Enum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'

class ProductUnit(str, enum.Enum):
    kg = 'kg'
    g = 'g'
    litre = 'litre'
    piece = 'piece'
    bouquet = 'bouquet'
    boite = 'boite'

class ProductCategory(str, enum.Enum):
    fruits = 'fruits'
    legumes = 'legumes'
    viandes = 'viandes'
    poissons = 'poissons'
    produits_laitiers = 'produits_laitiers'
    epicerie = 'epicerie'
    boissons = 'boissons'
    autres = 'autres'

# --- Models ---
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True))
    
    producer = relationship("Producer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="client")

class Producer(Base):
    __tablename__ = "producers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    farm_name = Column(String(200), nullable=False)
    location_city = Column(String(100), nullable=False)
    location_region = Column(String(100), nullable=False, index=True)
    location_lat = Column(Numeric(9, 6))
    location_lng = Column(Numeric(9, 6))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="producer")
    products = relationship("Product", back_populates="producer", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    producer_id = Column(UUID(as_uuid=True), ForeignKey("producers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Numeric(10, 3), nullable=False)
    unit = Column(Enum(ProductUnit), nullable=False, server_default='piece')
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    producer = relationship("Producer", back_populates="products")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(OrderStatus), nullable=False, server_default='draft', index=True)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    confirmed_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    client = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price_snapshot = Column(Numeric(10, 2), nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, server_default='pending', index=True)
    is_simulated_error = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    order = relationship("Order", back_populates="payment")
