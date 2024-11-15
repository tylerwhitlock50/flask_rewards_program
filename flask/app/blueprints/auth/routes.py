from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User, Retailer
from app.blueprints.auth.forms import LoginForm, RegistrationForm, LogoutForm
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from app.blueprints.auth import auth_bp
from datetime import datetime


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    elif form.errors:
        flash('Please correct the errors in the form.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    form.retailer.choices = [(r.id, r.name) for r in Retailer.query.all()]

    if form.validate_on_submit():
        # Create new user
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            phone=form.phone.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            address=form.address.data,
            referal_code=form.referal_code.data,
            tos_agreement=form.tos_agreement.data,
            tos_date=datetime.utcnow(),
            registration_date=datetime.utcnow(),
            updated_date=datetime.utcnow(),
            password_hash=generate_password_hash(form.password.data),
            retailer_id=form.retailer.data
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    form = LogoutForm()
    if form.validate_on_submit():
        logout_user()
        flash('You have been logged out.')
        return redirect(url_for('auth.login'))
    return render_template('auth/logout.html', form=form)

@auth_bp.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template('auth/terms_and_conditions.html')
