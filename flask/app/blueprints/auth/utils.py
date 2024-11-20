from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from app import mail
from app.models import User
from flask_mail import Message, Mail
from flask import url_for

def generate_password_reset_token(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user.email, salt='password-reset-salt')

def verify_password_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return User.query.filter_by(email=email).first()
    except:
        return None

def send_password_reset_email(recipient, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    msg = Message(
        subject="Password Reset Request",
        sender= current_app.config['MAIL_DEFAULT_SENDER'],  # Specify sender explicitly here
        recipients=[recipient]
    )
    msg.body = f"Please use the following link to reset your password: {reset_url}"
    mail.send(msg)