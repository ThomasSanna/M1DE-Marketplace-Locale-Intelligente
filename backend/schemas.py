from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from models import UserRole, ProductCategory, ProductUnit

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
