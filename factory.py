from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from spectree import SpecTree
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = SpecTree('flask', path='docs', security_schemes=[{'name': 'BearerAuth', 'data': {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}}])

from config import Config

def create_app () -> Flask:

    app = Flask(__name__)
    CORS(app)

    # ---------------- config
    
    Config().init_app(app)

    jwt.init_app(app)

    # ---------------- db

    db.init_app(app)

    from models import User, Product, ProductKind, Purchase, Tag, TagKind, TagLink, Rating

    migrate.init_app(app, db)

    # ---------------- routes

    from controllers import user_blueprint, product_blueprint, tag_blueprint, purchase_blueprint

    app.register_blueprint(user_blueprint)
    app.register_blueprint(product_blueprint)
    app.register_blueprint(tag_blueprint)
    app.register_blueprint(purchase_blueprint)

    api.register(app)

    return app
