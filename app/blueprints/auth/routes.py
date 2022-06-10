from flask import render_template, request, flash, redirect, url_for
from .forms import EditProfileForm, RegisterForm, LoginForm, SearchForm
from .import bp as auth
from ...models import User, Item
from flask_login import current_user, login_required, logout_user, login_user
import requests


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new_user_data={
                "first_name": form.first_name.data.title(),
                "last_name": form.last_name.data.title(),
                "email": form.email.data.lower(),
                "password": form.password.data,
                # "icon": f'{form.first_name.data.title()} {form.last_name.data.title()}'
            }
            new_user_object = User()
            new_user_object.from_dict(new_user_data)
            new_user_object.save()

        except:
            flash("There was an unexpected error when creating your account. Please try again", "danger")
            return render_template('register.html.j2', form=form)
        flash('Your account has been successfully created', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html.j2', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        u = User.query.filter_by(email=email).first()
        if u and u.check_hash(password):
            login_user(u)
            flash("Welcome to Sab's Shop!", 'success')
            return redirect(url_for('main.index'))
        flash("Incorrect email & password combination", "danger")
        return render_template("login.html.j2", form=form)
    return render_template("login.html.j2", form=form)

@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form=EditProfileForm()
    if request.method== 'POST' and form.validate_on_submit():
        new_user_data={"first_name": form.first_name.data.title(),
                "last_name": form.last_name.data.title(),
                "email": form.email.data.lower(),
                "password": form.password.data,
                "icon": form.icon
            }
        user = User.query.filter_by(email=new_user_data["email"]).first()
        if user and user.email != current_user.email:
            flash('Email is already in use. Please use another email', 'danger')
            return redirect(url_for('auth.edit_profile'))
        try:
            current_user.from_dict(new_user_data)
            current_user.save()
            flash('Your profile has been udpate', 'success')
        except:
            flash('There was an unexpected error updating your profile', 'danger')
            return redirect(url_for('auth.edit_profile'))
        return redirect(url_for('main.index'))
    return render_template('register.html.j2', form=form)

@auth.route('/logout')
@login_required
def logout():
    if current_user:
        logout_user()
        flash('You have successfully logged out', 'warning')
        return redirect(url_for('main.index'))

@auth.route('/shop', methods=['GET', 'POST'])
@login_required
def shop():
    form=SearchForm()
    if request.method == 'POST' and form.validate_on_submit():
        item = form.item.data
        search = Item.query.filter_by(item_name = item).first()
        # search = Item()
        if not search:
            url = f"http://127.0.0.1:5000/item/{item}"
            response = requests.get(url)
            if not response.ok:
                flash(f'We had an error on our end. Please try again.', 'danger')
                return render_template('one_item.html.j2', form=form)
            if not response.json()['item_name']:
                flash(f'We had an error loading your request. Check your spelling', 'danger')
            
            item_dict={
                "item_name":item['item_name'],
                "price":item['price'],
                "desc":item['desc'],
                "img":item['img'],
            }
            search.from_dict(item_dict)
            search.save()
                
        return render_template('one_item.html.j2', form=form, item=search)
    return render_template('one_item.html.j2', form=form)

@auth.route('/add_item/<string:item_name>')
@login_required
def add_item(item_name):
    item = Item.query.filter_by(item_name=item_name).first()
    current_user.add_item(item)
    flash(f'{item.item_name.title()} has been added to your cart', 'success')
    return redirect(url_for('auth.show_cart'))

@auth.route('/remove_item/<string:item_name>')
@login_required
def remove_item(item_name):
    item = Item.query.filter_by(item_name=item_name).first()
    current_user.remove_item(item)
    flash(f'{item.item_name.title()} has been removed from your cart', 'warning')
    return redirect(url_for('auth.show_cart'))


@auth.route('/show_cart')
@login_required
def show_cart():
    cart = current_user.show_cart()
    return render_template('show_cart.html.j2', cart=cart)

@auth.route('/clear_cart')
@login_required
def clear_cart():
    current_user.clear_cart()
    return render_template('show_cart.html.j2')