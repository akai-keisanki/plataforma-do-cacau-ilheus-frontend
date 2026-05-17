from datetime import datetime, date
import re
from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
from pydantic import BaseModel

from factory import db
from .utils import UserRole


class User (db.Model):
    __tablename__ = 'users'    
    id = db.Column(db.Integer, primary_key=True)

    # dados públicos

    name = db.Column(db.String(0x40), nullable=False, unique=False)
    bio = db.Column(db.String(0xFF), nullable=False, unique=False)
    roles = db.Column(db.Integer, nullable=False, unique=False)

    # dados privados

    email = db.Column(db.String(0x20), nullable=False, unique=True, index=True)
    phone_number = db.Column(db.String(0x1A), nullable=False, unique=True)
    cpf_or_cnpj = db.Column(db.String(0xE), nullable=False, unique=True)
    password_hash = db.Column(db.String(0x40), nullable=False, unique=False)

    @validates('email')
    def validate_email(self, key, value):

        value = value.strip()

        if not re.match('[a-zA-Z0-9_.]+@[a-zA-Z0-9_.]', value):
            raise ValueError('invalid email')

        return value.lower()

    @validates('phone_number')
    def validate_phone_number(self, key, value):

        return re.sub(r'\D', '', value)

    @validates('cpf_or_cnpj')
    def validade_cpf_cnpj(self, key, value):

        value = re.sub(r'\D', '', value)

        if len(value) not in [0xB, 0xE] or not value.isdigit():
            raise ValueError('invalid cpf')

        return value

    # datas

    birthday = db.Column(db.Date, nullable=False, unique=False)
    creation_date = db.Column(db.Date, default=lambda: datetime.utcnow().date(), nullable=False)

    # conexões
    
    products = db.relationship('Product', backref='vendor')
    purchases = db.relationship('Purchase', backref='client')

    def set_password (self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password (self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(UserLogin):
    name: str
    roles: list[str] = list(UserRole.to_strings(UserRole.get_all_roles_list()))
    birthday: date = "1969-12-31"
    cpf_or_cnpj: str
    phone_number: str

class UserQuery(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    roles: Optional[list[str]] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    birthday: Optional[date] = None
    cpf_or_cnpj: Optional[str] = None
    phone_number: Optional[str] = None
    roles: Optional[list[str]] = None
