from datetime import date
from typing import Optional

from pydantic import BaseModel, field_serializer, field_validator

from . import UserRole
from .models import ORMBase

class DefaultResponse(BaseModel):
    message: str

class AuthResponse(BaseModel):
    access_token: str

class UserPrivateResponse(ORMBase):
    email: str
    birthday: date = '1969-12-31'
    creation_date: date = '1969-12-31'
    cpf_or_cnpj: str
    phone_number: str

class ShorterProductResponse(ORMBase):
    name: str
    creation_date: date = '1969-12-31'

class UserShortResponse(ORMBase):
    name: str
    bio: str
    roles: list[str] = list(UserRole.to_strings(UserRole.get_all_roles_list()))

    @field_validator('roles', mode='before')
    @classmethod
    def val_roles(cls, roles: int):
        return list(UserRole.to_strings(UserRole.from_sum(roles))) if isinstance(roles, int) else roles

class UserPublicResponse(UserShortResponse):
    products: list[ShorterProductResponse]

class UserQueryResponse(BaseModel):
    users: list[UserShortResponse]

class ShortProductResponse(ORMBase):
    name: str
    price_cents: int
    product_kind_id: int
    vendor_id: int

class ProductResponse(ShortProductResponse):
    description: str
    tags: list[ORMBase]
    creation_date: date = '1969-12-31'

class ProductQueryResponse(BaseModel):
    products: list[ShortProductResponse]

class ProductKindResponse(ORMBase):
    name: str

class ProductKindQueryResponse(BaseModel):
    product_kinds: list[ProductKindResponse]

class PurchaseShortResponse(ORMBase):
    product_id: int
    rated: bool
    vendor_checked: bool
    status: Optional[str]
    purchase_date: date = '1969-12-31'

class PurchaseResponse(PurchaseShortResponse):
    amount: int
    notes: str
    minimum_deliver_date: Optional[date] = '1969-12-31'
    maximum_deliver_date: Optional[date] = '1969-12-31'
    rating_id: Optional[int]

class PurchaseQueryResponse(BaseModel):
    purchases: list[PurchaseShortResponse]

class TagResponse(ORMBase):
    name: str
    description: str
    tag_kind_id: int

class TagQueryResponse(BaseModel):
  tags: list[TagResponse]

class TagKindResponse(ORMBase):
  name: str

class TagKindQueryResponse(BaseModel):
  tag_kinds: list[TagKindResponse]
