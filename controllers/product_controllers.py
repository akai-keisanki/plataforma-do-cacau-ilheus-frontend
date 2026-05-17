from flask import Blueprint, request
from spectree import Response

from factory import db, api
from models import User, Product, ProductKind, Tag, TagLink
from models.product import ProductCreate, ProductQuery, ProductKindQuery
from models.utils import UserRole
from models.utils.responses import DefaultResponse, ProductResponse, ProductQueryResponse, ProductKindResponse, ProductKindQueryResponse
from .utils import wrap_response, require_roles
from .tag_controllers import delete_tag
from .purchase_controllers import delete_purchase

product_blueprint = Blueprint('product_controllers', __name__, url_prefix='/product')


def delete_product(product: Product) -> None:
    """
    Routine to delete a given product.

    Parameters
    ----------
    product : Product
        Product object to be deleted.
    """

    for tag_link in product.tag_links:

        tag = tag_link.tag
        db.session.delete(tag_link)

        if (not tag.tag_links) and (datetime.utcnow() - timedelta(days=730) >= tag.creation_date):
            delete_tag(tag)

    for purchase in product.purchases: delete_purchase(purchase)

    db.session.delete(product)


# CREATE

@product_blueprint.post('/')
@api.validate(json=ProductCreate, resp=Response(HTTP_201=DefaultResponse, HTTP_404=DefaultResponse), tags=['product'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.VENDOR])
def product_post(user: User):
    """
    Create a product.
    """

    name: str = request.json.get('name')
    description: str = request.json.get('description')
    price_cents: int = request.json.get('price_cents')
    ammount: int = request.json.get('ammount')
    tag_ids: list[int] = request.json.get('tag_ids')
    product_kind_id: int = request.json.get('product_kind_id')

    product_kind = ProductKind.query.filter_by(id=product_kind_id).first()
    if not product_kind: return 'Product kind not found', 404

    product = Product(vendor=user, name=name, description=description, price_cents=price_cents, ammount=ammount, product_kind=product_kind)

    for tag_id in tag_ids:
        tag = Tag.query.filter_by(id=tag_id).first()
        if not tag: return 'Tag not found', 404
        tag_link = TagLink()
        tag_link.tag = tag
        tag_link.product = product
        db.session.add(tag_link)

    db.session.add(product)
    db.session.commit()

    return 'Product created successfully!', 201

# READ

@product_blueprint.get('/<int:id>')
@api.validate(resp=Response(HTTP_200=ProductResponse), tags=['product'])
@wrap_response
def product_id_get(id: int):
    """
    Get product by ID.
    """

    product = Product.query.filter_by(id=id).first()
    if not product: return 'Product not found', 404

    return ProductResponse.model_validate(product).model_dump(), 200

@product_blueprint.get('/search')
@api.validate(query=ProductQuery, resp=Response(HTTP_200=ProductQueryResponse), tags=['product'])
@wrap_response
def product_search_get():
    """
    Search products by arguments.
    """
    
    query = Product.query

    minimum_price_cents: int | None = request.args.get('minimum_price_cents')
    if minimum_price_cents is not None:
        query = query.filter(Product.price_cents >= minimum_price_cents)

    maximum_price_cents: int | None = request.args.get('minimum_price_cents')
    if maximum_price_cents is not None:
        query = query.filter(Product.price_cents <= maximum_price_cents)

    tag_ids: list[int] | None = request.args.get('tag_ids')
    if tag_ids:
        for tag_id in tag_ids:
            query = query.filter(Product.tag_links.any(TagLink.tag_id == tag_id))

    product_kind_id: int | None = request.args.get('product_kind_id')
    if product_kind_id is not None:
        query = query.filter_by(product_kind_id=product_kind_id)

    for k in ['name', 'description']:

        v: str | None = request.args.get(k)

        if v:
            for word in v.split():
                if word: query = query.filter(getattr(Product, k).ilike(f"%{word}%"))

    products = query.all()

    return ProductQueryResponse(products=[product for product in products]).model_dump(), 200

@product_blueprint.get('/kind/search')
@api.validate(query=ProductKindQuery, resp=Response(HTTP_200=ProductKindQueryResponse), tags=['product'])
@wrap_response
def product_kind_search_get():
    """
    Search products kinds by arguments.
    """
    
    query = ProductKind.query

    name: str | None = request.args.get('name')

    if name:
        for word in name.split():
            if word: query = query.filter(ProductKind.name.ilike(f"%{word}%"))

    product_kinds = query.all()

    return ProductKindQueryResponse(product_kinds=[product_kind for product_kind in product_kinds]).model_dump(), 200

# UPDATE

# TODO: update user's product by ID if vendor

# DELETE

@product_blueprint.delete('/<int:id>')
@api.validate(resp=Response(HTTP_404=DefaultResponse, HTTP_200=DefaultResponse), tags=['product'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.VENDOR])
def product_id_delete(user: User, id: int):
    """
    Delete product by ID.
    """

    product = Product.query.filter_by(id=id).filter_by(vendor=user).first()
    if not product: return 'Product not found', 404

    delete_product(product)
    
    db.session.commit()

    return 'Product deleted successfully!', 200

@product_blueprint.delete('/mod/<int:id>')
@api.validate(resp=Response(HTTP_404=DefaultResponse, HTTP_200=DefaultResponse), tags=['product'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.MODERATOR])
def product_mod_id_delete(user: User, id: int):
    """
    Delete product by ID (by a MODERATOR).
    """

    product = Product.query.filter_by(id=id).first()
    if not product: return 'Product not found', 404

    delete_product(product)
    
    db.session.commit()

    return 'Product deleted successfully!', 200

