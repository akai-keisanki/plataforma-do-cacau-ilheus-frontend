from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from factory import db


class Product (db.Model):
    __tablename__ = 'products'    
    id = db.Column(db.Integer, primary_key=True)

    # display

    name = db.Column(db.String(0x80), nullable=False, unique=False)
    description = db.Column(db.String(0xFFF), nullable=False, unique=False)

    # números

    price_cents = db.Column(db.Integer, nullable=False, unique=False)
    ammount = db.Column(db.Integer, nullable=False, unique=False)
    medium_rating_percent = db.Column(db.Integer, nullable=True, default=None, unique=False)

    # datas

    creation_date = db.Column(db.Date, default=lambda: datetime.utcnow().date(), nullable=False)

    # conexões

    purchases = db.relationship('Purchase', backref='product')
    tag_links = db.relationship('TagLink', backref='product')
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_kind_id = db.Column(db.Integer, db.ForeignKey('product_kinds.id'), nullable=False)

class ProductKind (db.Model):
    __tablename__ = 'product_kinds'
    id = db.Column(db.Integer, primary_key=True)

    # identificadores

    name = db.Column(db.String(0x20), nullable=False, unique=False)

    # conexões

    products = db.relationship('Product', backref='product_kind')

class Tag (db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)

    # identificadores

    name = db.Column(db.String(0x20), nullable=False, unique=False)
    description = db.Column(db.String(0xFF), nullable=False, unique=False)

    # datas

    creation_date = db.Column(db.Date, default=lambda: datetime.utcnow().date(), nullable=False)

    # conexões

    tag_links = db.relationship('TagLink', backref='tag')
    tag_kind_id = db.Column(db.Integer, db.ForeignKey('tag_kinds.id'), nullable=False)

class TagKind (db.Model):
    __tablename__ = 'tag_kinds'    
    id = db.Column(db.Integer, primary_key=True)

    # identificadores

    name = db.Column(db.String(0x20), nullable=False, unique=False)

    # conexões

    tags = db.relationship('Tag', backref='tag_kind')


class TagLink (db.Model):
    __tablename__ = 'tag_links'    
    id = db.Column(db.Integer, primary_key=True)

    # conexões

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)

class ProductCreate(BaseModel):
    name: str
    description: str
    price_cents: int
    ammount: int
    tag_ids: list[int]
    product_kind_id: int

class ProductQuery(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    minimum_price_cents: Optional[int] = None
    maximim_price_cents: Optional[int] = None
    tag_ids: Optional[list[int]] = None
    product_kind_id: Optional[int] = None
    vendor_id: Optional[int] = None

class ProductKindQuery(BaseModel):
    name: Optional[str] = None

class TagCreate(BaseModel):
    name: str
    description: str
    tag_kind_id: int

class TagQuery(TagCreate):
    name: Optional[str] = None
    description: Optional[str] = None
    tag_kind_id: Optional[int] = None

class TagKindQuery(BaseModel):
    name: Optional[str] = None

