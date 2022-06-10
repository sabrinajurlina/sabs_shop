from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from ...models import User, Item, ItemUser

class LoginForm(FlaskForm):
    email = StringField('Enter Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Password Must Match')])#must equal password]
    submit = SubmitField('Register')

    def validate_email(form, field):
        same_email_user = User.query.filter_by(email = field.data).first()

        if same_email_user:
            raise ValidationError("That email is already registered. Please use another email or select 'Forgot Password' to reset your password")

class SearchForm(FlaskForm):
    item = StringField('Enter Item Name', validators=[DataRequired()])
    submit = SubmitField('Submit')