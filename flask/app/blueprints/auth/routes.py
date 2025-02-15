from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Retailer
from app.blueprints.auth.forms import LoginForm, RegistrationForm, LogoutForm
from app.extensions import db
#from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from app.blueprints.auth import auth_bp
from datetime import datetime
from app.blueprints.auth.utils import generate_password_reset_token, send_password_reset_email, verify_password_reset_token
from app import bcrypt
from app.extensions import log


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=str(form.email.data).lower()).first()
        log.info(f'User {user} attempted to log in at {datetime.now()}')
        
        if user:
            # Log retrieved hash and entered password
            log.debug(f'Retrieved hash: {user.password_hash}')
            log.debug(f'Entered password: {form.password.data}')
            log.debug(f'Hash type: {type(user.password_hash)}')
            log.debug(f'Calculated Hash: {bcrypt.generate_password_hash(form.password.data).decode("utf-8")}')
            
            # Calculate the hash of the entered password for comparison
            is_password_correct = bcrypt.check_password_hash(user.password_hash, form.password.data)
            log.debug(f'Password match: {is_password_correct}')
            
            if is_password_correct:
                login_user(user)
                flash('Logged in successfully.', 'success')
                log.info(f'User {user.email} logged in at {datetime.now()}')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password.', 'danger')
                log.info(f'Failed login attempt for {form.email.data} at {datetime.now()} - Incorrect password')
        else:
            flash('Invalid email or password.', 'danger')
            log.info(f'Failed login attempt for {form.email.data} at {datetime.now()} - User not found')

    elif form.errors:
        flash('Please correct the errors in the form.', 'danger')
        log.info(f'Form validation failed for {form.email.data} at {datetime.now()} with errors: {form.errors}')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    log.info(f'User attempted to register at {datetime.now()}')
    form = RegistrationForm()
    form.retailer.choices = [(r.id, r.name) for r in Retailer.query.all()]

    if form.validate_on_submit():
        log.info(f'User {form.email.data} successfully registered at {datetime.now()}')
        
        if form.password.data != form.confirm_password.data:
            log.warning(f'User registration failed at {datetime.now()} from {request.remote_addr}: Passwords do not match')
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('auth/register.html', form=form)
        try:
        # Create new user
            new_user = User(
                email=str(form.email.data).lower(),
                username=form.username.data,
                phone=form.phone.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                zip=form.zip.data,
                shirt_size=form.shirt_size.data,
                referal_code=form.referal_code.data,
                tos_agreement=form.tos_agreement.data,
                tos_date=datetime.utcnow(),
                registration_date=datetime.utcnow(),
                updated_date=datetime.utcnow(),
                password_hash=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
                retailer_id=form.retailer.data
            )

            db.session.add(new_user)
            db.session.commit()
            log.info(f'User {form.email.data} successfully registered at {datetime.now()}')

            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except IntegrityError:
            db.session.rollback()
            log.warning(f'User registration failed at {datetime.now()} from {request.remote_addr}: Email already exists')
            log.warning(f'User Registration failed at {datetime.now()} from {request.remote_addr}. Errors: {form.errors}')
            flash('Email is already registered. Please use a different email or log in.', 'danger')
            
    else:
        log.warning(f'User registration failed at {datetime.now()} from {request.remote_addr}. Errors: {form.errors}')
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.replace('_', ' ').capitalize()}: {error}", 'danger')
        

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    form = LogoutForm()
    log.info(f'User {current_user.email} logged out at {datetime.now()}')
    if form.validate_on_submit():
        logout_user()
        flash('You have been logged out.')
        return redirect(url_for('auth.login'))
    return render_template('auth/logout.html', form=form)

@auth_bp.route('/terms-and-conditions')
def terms_and_conditions():
    log.info(f'User viewed the terms and conditions at {datetime.now()}')
    return render_template('auth/terms_and_conditions.html')

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def request_password_reset():
    log.info(f'User requested a password reset at {datetime.now()}')
    if request.method == 'POST':
        email = str(request.form.get('email')).lower()
        user = User.query.filter_by(email=email).first()
        log.info(f'Password reset requested for {email} at {datetime.now()}')

        if user:
            token = generate_password_reset_token(user)  # Generate a secure token
            send_password_reset_email(user.email, token)  # Send reset email
            flash('Check your email for a password reset link.', 'info')
        else:
            flash('If this email is associated with an account, a password reset link has been sent.', 'info')
        
        return redirect(url_for('auth.login'))

    return render_template('auth/request_password_reset.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = verify_password_reset_token(token)
    if not user:
        log.info(f'Invalid or expired token used at {datetime.now()}')
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('auth.request_password_reset'))

    if request.method == 'POST':
        log.info(f'Password reset for {user.email} at {datetime.now()}')
        new_password = request.form.get('password')
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')  # Assuming bcrypt is used
        db.session.commit()
        flash('Your password has been reset. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    log.info(f'User viewed their profile at {datetime.now()}')
    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        user.city = request.form.get('city')
        user.state = request.form.get('state')
        user.zip = request.form.get('zip')
        user.shirt_size = request.form.get('shirt_size')
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        log.info(f'User {user.email} updated their profile at {datetime.now()}')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    log.info(f'User attempted to change their password at {datetime.now()}')
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if bcrypt.check_password_hash(current_user.password_hash, current_password):
            current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('Password updated successfully.', 'success')
            log.info(f'User {current_user.email} changed their password at {datetime.now()}')
            return redirect(url_for('auth.profile'))
        else:
            flash('Incorrect current password.', 'danger')
    return render_template('auth/change_password.html')


