from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from spectree import Response

from factory import db, api
from models import User
from models.user import UserCreate, UserLogin, UserQuery, UserUpdate
from models.utils import UserRole
from models.utils.responses import DefaultResponse, AuthResponse, UserPrivateResponse, UserQueryResponse, UserPublicResponse
from .utils import wrap_response
from .product_controllers import delete_product
from .purchase_controllers import delete_purchase

user_blueprint = Blueprint('user_controllers', __name__, url_prefix='/user')

# LOGON (CREATE)

@user_blueprint.post('/logon')
@api.validate(json=UserCreate, resp=Response(HTTP_201=DefaultResponse, HTTP_400=DefaultResponse), tags=['user'])
@wrap_response
def user_logon():
    """
    Logon.
    """

    name: str = request.json.get('name')
    email: str = request.json.get('email')
    password: str = request.json.get('password')
    roles: list[str] = request.json.get('roles')
    birthday: str = request.json.get('birthday')
    cpf_or_cnpj: str = request.json.get('cpf_or_cnpj')
    phone_number: str = request.json.get('phone_number')

    if db.session.query(User).filter_by(email=email).first(): return 'User with the provided email already exists', 400

    user = User(name=name, email=email, bio='', roles = UserRole.sum_roles(UserRole.from_strings(roles)) & ((1 << 2) - 1), birthday = datetime.strptime(birthday, '%Y-%m-%d'), cpf_or_cnpj = cpf_or_cnpj, phone_number = phone_number)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return 'User created successfully!', 201

# LOGIN

@user_blueprint.post('/login')
@api.validate(json=UserLogin, resp=Response(HTTP_200=AuthResponse), tags=['user'])
@wrap_response
def user_login():
    """
    Login with email and password.
    """

    email: str = request.json.get('email')
    password: str = request.json.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password): return 'Invalid credentials.', 401

    return AuthResponse(access_token=create_access_token(identity=str(user.id))).model_dump(), 200

# READ

@user_blueprint.get('/')
@jwt_required()
@api.validate(resp=Response(HTTP_200=UserPrivateResponse, HTTP_404=DefaultResponse), tags=['user'], security=[{'BearerAuth': []}])
@wrap_response
def user_get():
    """
    Get the current user's ID and private information.
    """

    user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not user: return 'User not found', 404

    return UserPrivateResponse.model_validate(user).model_dump(), 200

@user_blueprint.get('/<int:id>')
@api.validate(resp=Response(HTTP_200=UserPublicResponse), tags=['user'])
@wrap_response
def user_get_id(id: int):
    """
    Get information about an user by ID.
    """

    user = User.query.filter_by(id=id).first()
    if not user: return 'User not found', 404

    return UserPublicResponse.model_validate(user).model_dump(), 200

# TODO: list users by filters

@user_blueprint.get('/search')
@api.validate(query=UserQuery, resp=Response(HTTP_200=UserQueryResponse), tags=['user'])
@wrap_response
def user_search_get():
    """
    Search users by arguments.
    """

    query = User.query

    roles : list[str] | None = (request.args.get('roles'))
    if roles:
        query = query.filter(User.roles.op('&')(UserRole.sum_roles(UserRole.from_strings(roles))) != 0)

    for k in ['name', 'bio']:

        v: str | None = request.args.get(k)
        if v:
            for word in v.split():
                if word: query = query.filter(getattr(User, k).ilike(f"%{word}%"))

    users = query.all()

    return UserQueryResponse(users=[user for user in users]).model_dump(), 200


# UPDATE

@user_blueprint.put('/')
@jwt_required()
@api.validate(json=UserUpdate, resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse), tags=['user'], security=[{'BearerAuth': []}])
@wrap_response
def user_put():
    """
    Update the current user's information.
    """

    data = request.get_json()

    user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not user: return 'User not found', 404

    for k in ['name', 'bio', 'email']:
        v: str | None = data.get(k)
        if v: query = setattr(user, k, v)

    password: str | None = data.get('password')
    if password: user.set_password(password)

    birthday: str | None = data.get('birthday')
    if birthday: user.birthday = datetime.strptime(birthday, '%Y-%m-%d')

    cpf_or_cnpj: str | None = data.get('cpf_or_cnpj')
    if cpf_or_cnpj: user.cpf_or_cnpj = cpf_or_cnpj

    phone_number: str | None = data.get('phone_number')
    if phone_number: user.phone_number = phone_number

    # roles: list[str] | None = data.get('roles')
    # if roles: user.roles = UserRole.sum_roles(UserRole.from_strings(roles))

    db.session.commit()

    return 'User data updated successfully!', 200

# DELETE

@user_blueprint.delete('/')
@jwt_required()
@api.validate(resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse), tags=['user'], security=[{'BearerAuth': []}])
@wrap_response
def user_delete():
    """
    Delete the current user.
    """

    user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not user: return 'User not found', 404

    for product in user.products: delete_product(product)

    for purchase in user.purchases: delete_purchase(purchase)

    db.session.delete(user)

    db.session.commit()

    return 'User deleted successfully!', 200
