from flask import request, render_template, flash, redirect, url_for, current_app
from flask_login import current_user, login_required  # Import for session management
from app.models import PointCodes
from app.extensions import db
from .forms import EarnPointsForm
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app.extensions import log

from . import points_bp

@points_bp.route('/earn', methods=['GET', 'POST'])
@login_required  # Ensure only logged-in users can access this route
def earn_points():
    form = EarnPointsForm()  # Instantiate the form
    log.info(f'User {current_user.email} accessed the earn points page at {datetime.now()}')
    if request.method == 'GET':
        return render_template('points/earn.html', form=form)
    
    if request.method == 'POST':
        log.info(f'User {current_user.email} submitted the earn points form at {datetime.now()}')
        log.debug(f'Form data: {form.data}')
        log.debug(f'Request data: {request}')
        log.debug(f'Request files: {request.files}')
        log.debug(f'Request form: {request.form}')
        log.debug(f'Request values: {request.values}')

    if request.method == 'POST' and form.validate_on_submit():
        
        predefined_code = form.predefined_code.data
        if predefined_code == 'OTHER':
            code_str = form.code.data
        else:
            code_str = predefined_code

        receipt_file = form.receipt.data

        # Validate the code
        code = PointCodes.query.filter_by(code=code_str).first()
        
        if not code:
            flash("Points Code does not exist in the database.", "danger")
            return redirect(url_for('points_bp.earn_points'))

        if code.expiry_date and code.expiry_date <= datetime.utcnow():
            flash("This code has expired.", "warning")
            return redirect(url_for('points_bp.earn_points'))

        if code.one_time_use and code.use_count > 0:
            flash("This code has already been used.", "warning")
            return redirect(url_for('points_bp.earn_points'))
        
        if not code.active:
            flash("This code is deactivated.", "warning")
            return redirect(url_for('points_bp.earn_points'))

        # Save the receipt file
        filename = secure_filename(receipt_file.filename)
        receipt_dir = os.path.join(current_app.config['RECEIPT_UPLOAD_FOLDER'], str(current_user.id)+'_'+current_user.username)
        os.makedirs(receipt_dir, exist_ok=True)  # Create a user-specific folder if it doesn't exist
        file_path = os.path.join(receipt_dir, filename)
        receipt_file.save(file_path)

        # Log points for the current user
        try:
            current_user.log_points(code_str, file_path)
            log.info(f'User {current_user.email} successfully earned points for code {code_str} at {datetime.now()}')
            flash(f"Points successfully added for code {code_str}.", "success")
        except ValueError as e:
            flash(str(e), "danger")
            log.error(f'Error adding points for user {current_user.email} at {datetime.now()}: {str(e)}')

        return redirect(url_for('dashboard.dashboard'))
    
    else:
        log.error(f'User {current_user.email} encountered errors while trying to earn points at {datetime.now()}: {form.errors}')
        flash("An error occurred. Please check the form for errors.", "danger")

    return render_template('points/earn.html', form=form, errors=form.errors)

