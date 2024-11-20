from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask import redirect, url_for, flash
from flask_mail import Mail
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.', 'danger')
    return redirect(url_for('auth.login'))
