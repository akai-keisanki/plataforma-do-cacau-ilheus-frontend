from datetime import date

from app import app
from factory import db
from config import Config
from models import User, ProductKind, Tag, TagKind
from models.utils import UserRole

def populate_db():
    """
    Populate the database with initial data
    """

    with app.app_context():

        # ProductKind, Tag, TagKind

        product_kinds: str
        tags: str
        tag_kinds: str

        with open('database_pop/product_kinds.csv', 'r') as file:
            product_kinds = filter(lambda x: x[0] != '', map(lambda x: x.split(','), file.read().split('\n')[1:]))

        for data in product_kinds:
            product_kind = ProductKind(name=data[0])
            db.session.add(product_kind)

        with open('database_pop/tag_kinds.csv', 'r') as file:
            tag_kinds = filter(lambda x: x[0] != '', map(lambda x: x.split(','), file.read().split('\n')[1:]))

        for data in tag_kinds:
            tag_kind = TagKind(name=data[0])
            db.session.add(tag_kind)

        with open('database_pop/tags.csv', 'r') as file:
            tags = filter(lambda x: x[0] != '', map(lambda x: x.split(','), file.read().split('\n')[1:]))

        for data in tags:
            tag = Tag(name=data[0], description=data[1])
            tag.tag_kind = TagKind.query.filter_by(name=data[2]).first()
            db.session.add(tag)

        # User:

        user = User(name='admin', email=Config.ADM_EMAIL, bio='', roles=UserRole.ADMIN.value, birthday=date.fromisoformat('1900-01-01'), cpf_or_cnpj='00000000000', phone_number='0000000000000')
        user.set_password(Config.SECRET_KEY)

        db.session.add(user)

        # commit:

        db.session.commit()

if __name__ == '__main__': populate_db()
