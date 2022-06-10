# from flask import render_template
from app import db, login
from flask_login import UserMixin
from datetime import datetime as dt, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class ItemUser(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.item_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String)
    desc = db.Column(db.String)
    price = db.Column(db.Float)
    img = db.Column(db.String)

    def from_dict(self, data):
        for field in ['item_name', 'desc', 'price', 'img']:
            if field in data:
                setattr(self, field, data[field])

    # def from_dict(self, data):
    #     self.name = data['name']
    #     self.desc = data['desc']
    #     self.price = data['price']
    #     self.img = data['img']

    def to_dict(self):
        return {
            'item_id':self.item_id,
            'item_name':self.item_name,
            'desc':self.desc,
            'price':self.price,
            'img':self.img,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    password = db.Column(db.String)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    icon = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
    token = db.Column(db.String, index=True, unique=True)
    token_exp = db.Column(db.DateTime)
    cart = db.relationship(Item,
                secondary='item_user',
                backref='users',
                lazy='dynamic'
            )

    #### TOKEN AUTH ###

    def get_token(self, exp=86400):
        current_time = dt.utcnow()
        # give the user their back token if their is still valid
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        # if the token DNE or is exp
        self.token = secrets.token_urlsafe(32)
        self.token_exp = current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=61)
    
    @staticmethod
    def check_token(token):
        u  = User.query.filter_by(token=token).first()
        if not u or u.token_exp < dt.utcnow():
            return None
        return u

    ### END TOKEN AUTH ###
    
    def __repr__(self):
        return f'<User: {self.email} | {self.id}>'

    def __str__(self):
        return f'<User: {self.email} | {self.first_name} {self.last_name}>'

    def hash_password(self, original_password):
        return generate_password_hash(original_password)
    
    def check_hash(self, login_password):
        return check_password_hash(self.password, login_password)

    def from_dict(self, data):
        for field in ['first_name', 'last_name', 'email', 'password', 'created_on', 'icon', 'is_admin', 'token', 'token_exp']:
            if field =='password':
                self.password = self.hash_password(data['password'])
            elif field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        return {
            'id':self.id,
            'first_name':self.first_name,
            'last_name':self.last_name,
            'email':self.email,
            'created_on':self.created_on,
            'icon':self.icon,
            'is_admin':self.is_admin,
            'token':self.token
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_icon_url(self):
        return f'https://ui-avatars.com/api/?name={self.icon.split()[0]}+{self.icon.split()[1]}&background=A45A6F&color=F5FFFA.svg'

    #check if item in cart already
    def check_cart(self, item_to_check):
        if self.cart.count()>0:
            return self.cart.filter(Item.item_id == item_to_check.item_id).count()>0

    def add_item(self, item):
        if item not in self.cart:
            self.cart.append(item)
            db.session.commit()
        else:
            return "We're sorry, that item is no longer available. Please explore our other in stock items"

    def remove_item(self, item):
        if self.check_cart(item):
            self.cart.remove(item)
            db.session.commit()
        else:
            return 'There was an unexpected error. Please try again'
    
    def show_cart(self):
        if self.cart.count()>0:
            cart = self.cart
            return cart

    def total_items(self):
        return self.cart.count()
    

    def clear_cart(self):
        self.cart = []
        db.session.commit()
        return self.cart

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
