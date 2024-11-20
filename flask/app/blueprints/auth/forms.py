from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User, Retailer

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=30)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=15)])
    address = StringField('Address', validators=[DataRequired(), Length(max=100)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    state = StringField('State', validators=[DataRequired(), Length(max=2)])
    zip = StringField('ZIP Code', validators=[DataRequired(), Length(max=10)])
    referal_code = StringField('Referral Code', validators=[Length(max=30)])
    tos_agreement = BooleanField('I agree to the Terms of Service', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    retailer = SelectField('Retailer', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register')
    shirt_size = SelectField('Shirt Size', choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra Large'), ('XXL', 'Extra Extra Large')], validators=[DataRequired()])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

class LogoutForm(FlaskForm):
    submit = SubmitField('Logout')
