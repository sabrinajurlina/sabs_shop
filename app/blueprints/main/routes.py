from .import bp as main
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from .forms import SearchForm, LoginForm, RegisterForm
from app.models import User, Item, ItemUser

@main.route('/', methods=['GET'])
def index():
    # return render_template('home.html.j2')
    items = Item.query.all()
    items_as_dicts = [item.to_dict() for item in items]
    return render_template('home.html.j2', items=items_as_dicts)

@main.route('/all_items', methods=['GET'])
def all_items():
    items = Item.query.all()
    items_as_dicts = [item.to_dict() for item in items]
    return render_template('all_items.html.j2', items=items_as_dicts)

# @main.route('/item', methods = ['GET'])
# def one_item(id):
#     item = Item.query.filter_by(id).first()
#     return render_template('one_item.html.j2', id=id)