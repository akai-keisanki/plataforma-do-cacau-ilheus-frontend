from datetime import datetime

from flask import Blueprint, request
from spectree import Response

from factory import db, api
from models import User, Product, Purchase, Rating
from models.purchase import  PurchaseCreate, PurchaseQuery, PurchaseCheck, PurchaseEdit
from models.utils import UserRole
from models.utils.responses import DefaultResponse, PurchaseResponse, PurchaseQueryResponse
from .utils import wrap_response, require_roles

purchase_blueprint = Blueprint('purchase_controllers', __name__, url_prefix='/purchase')

def delete_purchase(purchase: Purchase) -> None:
    """
    Routine to delete a given purchase.

    Parameters
    ----------
    purchase : Purchase
        Purchase object to be deleted.
    """

    if purchase.rating: db.session.delete(purchase.rating)

    db.session.delete(purchase)


# CREATE

@purchase_blueprint.post('/')
@api.validate(json=PurchaseCreate, resp=Response(HTTP_201=DefaultResponse, HTTP_404=DefaultResponse), tags=['purchase'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.CLIENT])
def purchase_post(user: User):
    """
    Create a purchase.
    """

    product_id: int = request.json.get('product_id')
    amount: int = request.json.get('amount')
    notes: str = request.json.get('notes')

    product = Product.query.filter_by(id=product_id).first()
    if not product: return 'Product not found', 404

    purchase = Purchase(client=user, notes=notes, product=product, amount=amount, vendor_checked=False, rated=False)

    db.session.add(purchase)
    db.session.commit()

    return 'Purchase created successfully!', 201

# READ

# TODO: get private purchase by ID (client)

@purchase_blueprint.get('/client/<int:id>')
@api.validate(resp=Response(HTTP_200=PurchaseResponse, HTTP_404=DefaultResponse), tags=['purchase'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.CLIENT])
def purchase_client_id_get(user: User, id: int):
    """
    Get purchase data by ID by a client.
    """

    purchase = Purchase.query.filter_by(id=id).filter_by(client=user).first()
    if not purchase: return 'Purchase not found', 404

    return PurchaseResponse.model_validate(purchase).model_dump(), 200

@purchase_blueprint.get('/vendor/<int:id>')
@api.validate(resp=Response(HTTP_200=PurchaseResponse, HTTP_404=DefaultResponse), tags=['purchase'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.VENDOR])
def purchase_vendor_id_get(user: User, id: int):
    """
    Get purchase data by ID by a vendor.
    """

    purchase = Purchase.query.filter_by(id=id).filter(Purchase.product.vendor == user).first()
    if not purchase: return 'Purchase not found', 404

    return PurchaseResponse.model_validate(purchase).model_dump(), 200

@purchase_blueprint.get('/of_product/<int:id>')
@api.validate(resp=Response(HTTP_200=PurchaseQueryResponse, HTTP_404=DefaultResponse), tags=['purchase'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.VENDOR])
def purchase_of_product_id(user: User, id: int):
    """
    List purchases by product ID by a vendor.
    """

    product = Product.query.filter_by(id=id).filter_by(vendor=user).first()
    if not product: return 'Product not found', 404

    return PurchaseQueryResponse(purchases=product.purchases).model_dump(), 200

@purchase_blueprint.get('/search')
@api.validate(query=PurchaseQuery, resp=Response(HTTP_200=PurchaseQueryResponse, HTTP_404=DefaultResponse), tags=['purchase'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.CLIENT])
def purchase_search(user: User):
    """
    Search purchases by a client.
    """

    query = Purchase.query.filter_by(client=user)

    rated: bool | None = request.args.get('rated')
    if rated is not None: query.filter_by(rated=rated)

    vendor_checked: bool | None = request.args.get('vendor_checked')
    if vendor_checked is not None: query.filter_by(vendor_checked=vendor_checked)

    product_id: int | None = request.args.get('product_id')
    if product_id is not None: query.filter_by(product_id=product_id)

    minimum_purchase_date: str | None = request.args.get('minimum_purchase_date')
    if minimum_purchase_date: query.filter(Purchase.purchase_date >= minimum_purchase_date)

    maximum_purchase_date: str | None = request.args.get('maximum_purchase_date')
    if maximum_purchase_date: query.filter(Purchase.purchase_date <= maximum_purchase_date)

    status: str | None = request.args.get('status')
    if status:
        for word in v.split():
            if word: query = query.filter(Purchase.status.ilike(f"%{word}%"))

    purchases = query.all()

    return PurchaseQueryResponse(purchases=[purchase for purchase in purchases]).model_dump()

# UPDATE

@purchase_blueprint.put('/check/<int:id>')
@api.validate(json=PurchaseCheck, resp=Response(HTTP_200=DefaultResponse, HTTP_304=DefaultResponse, HTTP_404=DefaultResponse), tags=['purchase'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.VENDOR])
def purchase_check_id(user: User, id: int):
    """
    Check purchase and set dates by ID by a vendor.
    """

    purchase = Purchase.query.filter_by(id=id).filter(Purchase.product.vendor == user).first()
    if not purchase: return 'Purchase not found', 404

    if purchase.vendor_checked: return 'Purchase already checked.', 304

    minimum_deliver_date: str = request.json.get('minimum_deliver_date')
    maximum_deliver_date: str = request.json.get('maximum_deliver_date')
    status: str | None = request.json.get('status')

    if (not minimum_deliver_date) or (not maximum_deliver_date): return 400

    purchase.vendor_checked = True

    purchase.minimum_deliver_date = datetime.strptime(minimum_deliver_date, '%Y-%m-%d')
    purchase.maximum_deliver_date = datetime.strptime(maximum_deliver_date, '%Y-%m-%d')

    if status: purchase.status = status

    purchase.product.ammount -= purchase.ammount

    db.session.commit()

    return 'Purchase checked successfully!', 200

@purchase_blueprint.put('/<int:id>')
@api.validate(json=PurchaseEdit, resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse), tags=['purchase'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.VENDOR])
def purchase_id_put(user: User, id: int):
    """
    Edit purchase status by ID by a vendor.
    """

    purchase = Purchase.query.filter_by(id=id).filter(Purchase.product.vendor == user).first()
    if not purchase: return 'Purchase not found', 404

    status: str | None = request.json.get('status')
    if status: purchase.status = status

    db.session.commit()

    return 'Purchase updated successfully!', 200

# DELETE

@purchase_blueprint.delete('/<int:id>')
@api.validate(resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse), tags=['purchase'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.CLIENT])
def purchase_id_delete(user: User, id: int):
    """
    Delete purchase by ID by a client if it is not checked by the vendor.
    """

    purchase = Purchase.query.filter_by(id=id).filter_by(client=user).first()
    if not purchase: return 'Purchase not found', 404

    if purchase.vendor_checked:
        return 'Purchase is vendor_checked and cannot be deleted.', 409

    delete_purchase(purchase)

    db.session.commit()

    return 'Purchase deleted successfully!', 200
