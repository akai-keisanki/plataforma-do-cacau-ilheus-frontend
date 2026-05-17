from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

from factory import db


class Purchase (db.Model):
    __tablename__ = 'purchases'    
    id = db.Column(db.Integer, primary_key=True)

    # texto

    notes = db.Column(db.String(0xFFF), nullable=False, unique=False)
    status = db.Column(db.String(0x40), nullable=True, unique=False)

    # checks

    vendor_checked = db.Column(db.Boolean, nullable=False, unique=False)
    rated = db.Column(db.Boolean, nullable=False, unique=False)

    # datas

    mininum_deliver_date = db.Column(db.Date, nullable=True)
    maximum_deliver_date = db.Column(db.Date, nullable=True)
    purchase_date = db.Column(db.Date, default=lambda: datetime.utcnow().date(), nullable=False)

    # conexões

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.relationship('Rating', backref='purchase', uselist=False)


class Rating (db.Model):
    __tablename__ = 'ratings'    
    id = db.Column(db.Integer, primary_key=True)
    
    # avaliação

    description = db.Column(db.String(0xFF), nullable=False, unique=False)
    percentage = db.Column(db.Integer, nullable=False, unique=False)

    # datas

    rating_date = db.Column(db.Date, default=lambda: datetime.utcnow().date(), nullable=False)

    # conexão

    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

class PurchaseCreate(BaseModel):
    product_id: int
    amount: int
    notes: str

class PurchaseQuery(BaseModel):
    vendor_checked: Optional[bool] = None
    rated: Optional[bool] = None
    status: Optional[str] = None
    product_id: Optional[int] = None
    minimum_purchase_date: Optional[date] = None
    maximum_purchase_date: Optional[date] = '1969-12-31'

class PurchaseCheck(BaseModel):
    minimum_deliver_date: date = '1969-12-31'
    maximum_deliver_date: date = '1969-12-31'
    status: Optional[str] = None

class PurchaseEdit(BaseModel):
    status: Optional[str] = None