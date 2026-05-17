from functools import wraps

from flask import Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import User
from models.utils import UserRole
from models.utils.responses import DefaultResponse

def wrap_response(route):
    """
    Wrap the return to propper responses.
    """

    @wraps(route)
    def wrapper(*args, **kwargs) -> tuple[Response, int]:

        response = route(*args, **kwargs)
        error_code = 200

        if isinstance(response, tuple): response, error_code = response

        if isinstance(response, str): response = DefaultResponse(message=response).model_dump()

        return jsonify(response), error_code

    return wrapper

class require_roles:
    """
    Require JWT and all the roles provided and wrap response.
    """

    roles: int

    def __init__(self, roles: list[UserRole]):
        self.roles = UserRole.sum_roles(roles)

    def __call__(self, route):

        @wraps(route)
        @jwt_required()
        def wrapper(*args, **kwargs):

            user = User.query.filter_by(id=int(get_jwt_identity())).first()
            if not user: return 'User not found', 404

            if self.roles & user.roles != self.roles: return 'User misses roles.', 403

            return route(user, *args, **kwargs)

        return wrapper
