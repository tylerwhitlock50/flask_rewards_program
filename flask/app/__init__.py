from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from app.extensions import db, migrate, login_manager
from app.blueprints.auth import auth_bp
from app.blueprints.points import points_bp
from app.blueprints.dashboard import dashboard_bp
from app.blueprints.rewards import rewards_bp
from app.blueprints.admin import admin_bp
from datetime import datetime

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models here to avoid circular imports
    from app.models import User, Retailer
    from app.demo_data import seed_demo_data

    # Create tables and seed demo data in development environment
    if app.config['ENV'] == 'development':
        with app.app_context():
            db.create_all()
            if not Retailer.query.filter_by(name='Demo Retailer').first():
                seed_demo_data()

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(points_bp, url_prefix='/points')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(rewards_bp, url_prefix='/rewards')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.dashboard'))
        return render_template('index.html')

    return app
