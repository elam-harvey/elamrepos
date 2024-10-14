from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField,
                     BooleanField, TextAreaField, IntegerField, DecimalField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from farmblog.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ProductCreationForm(FlaskForm):
    f_image = FileField('Product', validators=[FileAllowed(['jpg', 'png'])])
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[DataRequired()])
    new_quantity = StringField('New Quantity', validators=[Optional()])
    price = DecimalField('Price(KES)', validators=[DataRequired()])
    new_price = DecimalField('New Price(KES)', validators=[Optional()])
    submit = SubmitField('Create')

class ProductEditForm(FlaskForm):
    f_image = FileField('Product', validators=[FileAllowed(['jpg', 'png'])])
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[DataRequired()])
    new_quantity = StringField('New Quantity', validators=[DataRequired()])
    price = DecimalField('Price(KES)', validators=[DataRequired()])
    new_price = DecimalField('New Price(KES)', validators=[DataRequired()])
    submit = SubmitField('Edit')

    # logic to handle the update form
    def validate_quantity(self, quantity):
        if quantity.data < 0:
            raise ValidationError('Quantity cannot be negative')
        else:
            quantity.data != new_quantity
            raise ValidationError('Quantity updated successfully')

    def validate_price(self, price):
        if price.data != new_price:
            raise ValidationError('Price updated successfully')

class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
    
