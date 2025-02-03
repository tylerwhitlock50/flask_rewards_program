from flask import request, render_template, flash, redirect, url_for, current_app
from flask_login import current_user, login_required  # Import for session management
from app.extensions import db
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app.extensions import log

from . import rewards_bp

@rewards_bp.route('/redeem', methods=['GET', 'POST'])
@login_required
def redeem_points():
    balance = current_user.get_point_balance()
    gift_card_value = 1.25  # Supercomp Gift Card value per point
    visa_value = 1       # VISA Gift Card value per point
    log.info(f'User {current_user.email} accessed the redeem points page at {datetime.now()}')
    
    if request.method == 'POST':
        redemption_type = request.form.get('redemption_type')
        points_to_redeem = request.form.get('points_to_redeem', 0)
        log.info(f'User {current_user.email} attempted to redeem {points_to_redeem} points at {datetime.now()}')

        if points_to_redeem == '':
            flash('Please enter the number of points to redeem.', 'danger')
            log.warning(f'User {current_user.email} attempted to redeem points without entering a value at {datetime.now()}')
            return redirect(url_for('rewards_bp.redeem_points'))
        points_to_redeem = int(points_to_redeem)
        if points_to_redeem < current_app.config['MINIMUM_REDEMPTION']:
            flash('Minimum redemption is 500 points.', 'danger')
            log.warning(f'User {current_user.email} attempted to redeem less than the minimum at {datetime.now()}')
            return redirect(url_for('rewards_bp.redeem_points'))

        if points_to_redeem <= 0:
            flash('Please redeem a valid number of points.', 'danger')
            log.warning(f'User {current_user.email} attempted to redeem an invalid number of points at {datetime.now()}')
            return redirect(url_for('rewards_bp.redeem_points'))

        if points_to_redeem > balance:
            flash('You do not have enough points to redeem.', 'danger')
            log.warning(f'User {current_user.email} attempted to redeem more points than they have at {datetime.now()}')
            return redirect(url_for('rewards_bp.redeem_points'))

        if redemption_type == 'credit':
            redemption_value = points_to_redeem * gift_card_value
            description = 'Supercomp Gift Card'
            log.info(f'User {current_user.email} redeemed {points_to_redeem} points for a Supercomp Gift Card at {datetime.now()}')
        elif redemption_type == 'visa':
            redemption_value = points_to_redeem * visa_value
            description = 'VISA Gift Card'
            log.info(f'User {current_user.email} redeemed {points_to_redeem} points for a VISA Gift Card at {datetime.now()}')
        else:
            flash('Invalid redemption type selected.', 'danger')
            log.warning(f'User {current_user.email} attempted to redeem points with an invalid redemption type at {datetime.now()}')
            return redirect(url_for('rewards_bp.redeem_points'))
        try:
            current_user.redeem_points(points_to_redeem, redemption_type)
            flash(f'Successfully redeemed {points_to_redeem} points for a {description} worth ${redemption_value:.2f}.', 'success')
            log.info(f'User {current_user.email} successfully redeemed {points_to_redeem} points for a {description} at {datetime.now()}')
        except Exception as e:
            flash(f'An error occurred while redeeming points: {str(e)}', 'danger')
            log.error(f'Error redeeming points for user {current_user.email} at {datetime.now()}: {str(e)}')
        return redirect(url_for('dashboard.dashboard'))

    return render_template(
        'redeem/redeem.html',
        balance=balance,
        current_app = current_app
    )

