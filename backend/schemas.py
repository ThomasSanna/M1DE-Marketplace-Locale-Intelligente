from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID
from models import UserRole, ProductCategory, ProductUnit, PaymentStatus, OrderStatus

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ---- User Schemas ---- #
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ---- Producer Schemas ---- #
class ProducerBase(BaseModel):
    farm_name: str
    location_city: str
    location_region: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    description: Optional[str] = None

class ProducerCreate(ProducerBase):
    pass

class ProducerResponse(ProducerBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

# ---- Product Schemas ---- #
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: ProductCategory
    price: float = Field(..., ge=0)
    stock_quantity: float = Field(..., ge=0)
    unit: ProductUnit = ProductUnit.piece

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ProductCategory] = None
    price: Optional[float] = Field(None, ge=0)
    stock_quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[ProductUnit] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: UUID
    producer_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---- Payment Schemas ---- #
PaymentSimulationScenario = Literal[
    "auto",
    "success",
    "insufficient_funds",
    "provider_timeout",
    "fraud_suspected",
    "network_error",
]


class PaymentSimulationRequest(BaseModel):
    order_id: UUID
    payment_method: Literal["card", "wallet", "bank_transfer"] = "card"
    idempotency_key: Optional[str] = Field(default=None, min_length=8, max_length=64)
    simulate_scenario: PaymentSimulationScenario = "auto"
    processing_delay_ms: int = Field(default=120, ge=0, le=2000)


class PaymentSimulationResponse(BaseModel):
    payment_id: UUID
    order_id: UUID
    status: PaymentStatus
    order_status: OrderStatus
    amount: float
    idempotency_key: Optional[str] = None
    simulated_latency_ms: int
    retryable: bool = False
    provider_reference: str


class PaymentErrorResponse(BaseModel):
    error_code: str
    message: str
    retryable: bool
    order_id: UUID
    provider_reference: str
