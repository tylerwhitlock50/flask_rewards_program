from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import current_user
from app.extensions import db, migrate, login_manager, mail, bcrypt, log
from app.blueprints.auth import auth_bp
from app.blueprints.points import points_bp
from app.blueprints.dashboard import dashboard_bp
from app.blueprints.rewards import rewards_bp
from app.blueprints.admin import admin_bp
from datetime import datetime

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    log.info(f'App started at {datetime.now()}')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

    @app.cli.command('seed_data')
    def seed_data():
        from app.seed import seed_data
        seed_data()


    @app.before_request
    def check_user_active():
        # List of exempt routes
        exempt_routes = ['auth.logout', 'auth.register', 'auth.login', 'static']

        if request.endpoint not in exempt_routes:
            if current_user.is_authenticated and not current_user.is_active:
                flash('Your account is inactive. Please contact an administrator.', 'danger')
                return render_template('auth.login')

    # Import models here to avoid circular imports
    from app.models import User, Retailer
    from app.demo_data import seed_demo_data

    # Create tables and seed demo data in development environment
    if app.config['ENV'] == 'development':
        with app.app_context():
            db.create_all()
            if not Retailer.query.filter_by(name='Demo Retailer').first():
                seed_demo_data()

    if app.config['ENV'] == 'production':
        with app.app_context():
            db.create_all()


    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(points_bp, url_prefix='/points')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(rewards_bp, url_prefix='/rewards')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    log.info('Blueprints registered')

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.dashboard'))
        return render_template('index.html')

    return app
