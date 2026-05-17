from datetime import datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from spectree import Response

from factory import db, api
from models import User, Tag, TagLink, TagKind
from models.product import TagCreate, TagQuery, TagKindQuery
from models.utils import UserRole
from models.utils.responses import TagResponse, TagQueryResponse, TagKindQueryResponse, DefaultResponse
from .utils import wrap_response, require_roles

tag_blueprint = Blueprint('tag_controllers', __name__, url_prefix='/tag')

# TODO: Create a way to delete tags that are no longer in use for a year


def delete_tag(tag: Tag) -> None:
    """
    Routine to delete a given tag.

    Parameters
    ----------
    tag : Tag
        Tag object to be deleted.
    """

    for tag_link in tag.tag_links:
        db.session.delete(tag_link)

    db.session.delete(tag)


# CREATE

@tag_blueprint.post('/')
@api.validate(json=TagCreate, resp=Response(HTTP_201=DefaultResponse, HTTP_404=DefaultResponse), tags=['tag'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.VENDOR])
def tag_post(user):
    """
    Create a tag.
    """

    name: str = request.json.get('name')
    description: str = request.json.get('description')
    tag_kind_id: int = request.json.get('tag_kind_id')

    tag_kind = TagKind.query.filter_by(id=tag_kind_id).first()
    if not tag_kind: return 'Tag kind not found', 404

    tag = Tag(name=name, description=description, tag_kind=tag_kind)

    db.session.add(tag)
    db.session.commit()

    return 'Tag created successfully!', 201

# READ

@tag_blueprint.get('/<int:id>')
@api.validate(resp=Response(HTTP_200=TagResponse, HTTP_404=DefaultResponse), tags=['tag'])
@wrap_response
def tag_id_get(id: int):
    """
    Get tag by ID.
    """

    tag = Tag.query.filter_by(id=id).first()

    if not tag: return 'Tag not found', 404

    return TagResponse.model_validate(tag).model_dump(), 200

@tag_blueprint.get('/search')
@api.validate(query=TagQuery, resp=Response(HTTP_200=TagQueryResponse), tags=['tag'])
@wrap_response
def tag_search_get():
    """
    Search tags by arguments.
    """
    
    query = Tag.query

    for k in ['name', 'description']:

        v: str | None = request.args.get(k)

        if v:
            for word in v.split():
                if word: query = query.filter(getattr(Tag, k).ilike(f"%{word}%"))

    tag_kind_id: int | None = request.args.get('tag_kind_id')
    if tag_kind_id:
        query = query.filter_by(tag_kind_id=tag_kind_id)

    tags = query.all()

    # TODO: check if tags are not used and are old to remove them if so

    tags = []

    for tag in tags:

        if (not tag.tag_links) and (datetime.utcnow() - timedelta(days=730) >= tag.creation_date):
            delete_tag(tag)
            continue

        tags.append(tag)

    return TagQueryResponse(tags=tags).model_dump(), 200


@tag_blueprint.get('/kind/search')
@api.validate(query=TagKindQuery, resp=Response(HTTP_200=TagKindQueryResponse), tags=['tag'])
@wrap_response
def tag_kind_search_get():
    """
    Search tag kinds by arguments.
    """
    
    query = TagKind.query

    name: str | None = request.args.get('name')

    if name:
        for word in name.split():
            if word: query = query.filter(TagKind.name.ilike(f"%{word}%"))

    tag_kinds = query.all()

    return TagKindQueryResponse(tag_kinds=[tag_kind for tag_kind in tag_kinds]), 200



# UPDATE

# TODO: update tag by ID if MODERATOR

# DELETE

@tag_blueprint.delete('/mod/<int:id>')
@api.validate(resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse), tags=['tag'], security=[{'BearerAuth': []}])
@wrap_response
@require_roles([UserRole.MODERATOR])
def tag_mod_id_delete(user: User, id: int):
    """
    Delete tag by ID (by a MODERATOR).
    """

    tag = Tag.query.filter_by(id=id).first()
    if not tag: return 'Tag not found', 404

    delete_tag(tag)
    
    db.session.commit()

    return 'Tag deleted successfully!', 200

