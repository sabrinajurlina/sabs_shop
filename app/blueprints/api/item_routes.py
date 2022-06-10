from . import bp as api
from app.blueprints.auth.auth import token_auth
from flask import request, make_response, g, abort
from ...models import *
from ...helpers import require_admin

### get all items from shop ###
@api.get('/item')
def get_items():
    items = Item.query.all()
    items_dicts = [item.to_dict() for item in items]
    return make_response({"items":items_dicts}, 200)

### get one item by id ###
@api.get('/item/<int:id>')
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        abort(404)
    item_dict = item.to_dict()
    return make_response({"item":item_dict}, 200)

@api.post('/item')
@token_auth.login_required()
@require_admin
def post_item():
    #get payload from request
    item_dict = request.get_json()
    #ensure payload has all values we need
    if not all(key in item_dict for key in ('item_name', 'desc', 'price', 'img')):
        abort(400)
    #create an empty Item object
    item = Item()
    #set attributes of that item to the payload
    item.from_dict(item_dict)
    #save
    item.save()
    #send response to user
    return make_response(f"Item {item.item_name} was created with an ID of {item.item_id}", 200)

@api.put("/item/<int:item_id>")
@token_auth.login_required()
@require_admin
def put_item(item_id):
    item_dict = request.get_json()
    item = Item.query.get(item_id)
    if not item:
        abort(404)
    item.from_dict(item_dict)
    item.save()
    return make_response(f"Item {item.item_name} with ID {item.item_id} has been updated", 200)

@api.delete('/item/<int:item_id>')
@token_auth.login_required()
@require_admin
def delete_item(id):
    item_to_delete = Item.query.get(id)
    if not item_to_delete:
        abort(404)
    item_to_delete.delete()
    return make_response(f"Item with id: {id} has been deleted", 200)