# app/blueprints/admin/routes.py
from . import admin_bp
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, PointsLog, RedemptionLog
from app.extensions import db
from app.blueprints.admin.forms import ModifyTransactionForm, MarkGiftCardSentForm, DeleteTransactionForm

@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin & current_user.is_active:
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('index'))

@admin_bp.route('/admin', methods=['GET','POST'])
def admin_dashboard():
    participants = User.query.all()
    unsent_redemptions = RedemptionLog.query.filter_by(gift_card_sent=False).all()
    unreviewed_receipts = PointsLog.query.filter(
        PointsLog.approved == False,
        PointsLog.points > 0,
        PointsLog.file_reference.isnot(None),
        PointsLog.approved_by.is_(None)
    ).count()

    if request.method == 'POST':
        redemption_id = request.form.get('redemption_id')
        redemption = RedemptionLog.query.get_or_404(redemption_id)
        redemption.gift_card_sent = True
        db.session.commit()
        flash(f'Redemption for {redemption.description} marked as sent.', 'success')
        return redirect(url_for('admin_bp.admin_dashboard'))

    return render_template('admin/dashboard.html', participants=participants, unsent_redemptions=unsent_redemptions, unreviewed_receipts=unreviewed_receipts)

@admin_bp.route('/admin/transactions/<int:user_id>', methods=['GET', 'POST'])
def user_transactions(user_id):
    form = MarkGiftCardSentForm()
    form_del = DeleteTransactionForm()  
    user = User.query.get_or_404(user_id)
    points_logs = PointsLog.query.filter_by(user_id=user_id).all()
    redemptions = RedemptionLog.query.filter_by(user_id=user_id).all()
    return render_template('admin/transactions.html', user=user, points_logs=points_logs, redemptions=redemptions, form=form, form_del =form_del )

@admin_bp.route('/admin/redemptions/mark_sent/<int:redemption_id>', methods=['POST'])
def mark_gift_card_sent(redemption_id):
    print('route_called')
    redemption = RedemptionLog.query.get_or_404(redemption_id)
    print(redemption)
    redemption.mark_sent()
    flash('Gift card marked as sent.', 'success')
    return redirect(url_for('admin_bp.admin_dashboard', user_id=redemption.user_id))


@admin_bp.route('/admin/transactions/edit/<int:log_id>', methods=['GET', 'POST'])
def edit_transaction(log_id):
    log = PointsLog.query.get_or_404(log_id)
    form = ModifyTransactionForm(obj=log)

    if form.validate_on_submit():
        # Calculate the difference between new and old original points
        original_difference = form.original_points.data - log.original_points

        # Adjust log.points accordingly
        log.points += original_difference
        if log.points < 0:
            flash('Transaction cannot result in negative points.', 'danger')
            return redirect(url_for('admin_bp.edit_transaction', log_id=log_id))

        # Update the log details
        log.original_points = form.original_points.data
        log.description = form.description.data

        # Commit changes
        db.session.commit()
        flash('Transaction updated successfully.', 'success')
        return redirect(url_for('admin_bp.user_transactions', user_id=log.user_id))

    return render_template('admin/edit_transaction.html', form=form, log=log)

@admin_bp.route('/admin/transactions/delete/<int:log_id>', methods=['POST'])
def delete_transaction(log_id):
    log = PointsLog.query.get_or_404(log_id)
    if log.points == log.original_points:
        db.session.delete(log)
        db.session.commit()
        flash('Transaction deleted successfully.', 'success')
    else:
        flash('Transaction cannot be deleted. Points Already Used', 'danger')
    return redirect(url_for('admin_bp.user_transactions', user_id=log.user_id))

@admin_bp.route('/admin/receipts/<int:user_id>', methods=['GET'])
def user_receipts(user_id):
    # Placeholder for receipt review logic
    flash('Receipt review functionality coming soon.', 'info')
    return redirect(url_for('admin_bp.admin_dashboard'))


@admin_bp.route('/admin/receipts/review', methods=['GET', 'POST'])
def review_receipts():
    log = PointsLog.query.filter(
        PointsLog.approved == False,
        PointsLog.points > 0,
        PointsLog.file_reference.isnot(None),
        PointsLog.approved_by.is_(None)
    ).first()

    if not log:
        flash('No receipts left to review.', 'info')
        return redirect(url_for('admin_bp.admin_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'approve':
            flash('Receipt approved.', 'success')
            log.approved = True
            log.approved_by = current_user.id
            db.session.commit()
        elif action == 'deny':
            log.points = 0
            log.original_points = 0
            log.description += ' (Rejected)'
            log.approved_by = current_user.id
            db.session.commit()
            flash('Receipt denied and points set to 0.', 'danger')

        return redirect(url_for('admin_bp.review_receipts'))

    return render_template('admin/review_receipts.html', log=log)

@admin_bp.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    # Input sanitization function
    def clean(input):
        input = str(input).strip() if input else None  # Strip whitespace if input is not None
        return input if input and input != 'None' else None  # Return None for empty or "None"

    if request.method == 'POST':
        # Apply 'clean' to all fields to sanitize input
        user.first_name = clean(request.form.get('first_name'))
        user.last_name = clean(request.form.get('last_name'))
        user.email = clean(request.form.get('email'))
        user.phone = clean(request.form.get('phone'))
        user.address = clean(request.form.get('address'))
        user.shirt_size = clean(request.form.get('shirt_size'))
        user.salesep_id = clean(request.form.get('salesep_id'))
        user.territory_id = clean(request.form.get('territory_id'))
        user.customer_group = clean(request.form.get('customer_group'))
        user.team_id = clean(request.form.get('team_id'))
        user.user_1 = clean(request.form.get('user_1'))
        user.user_2 = clean(request.form.get('user_2'))
        user.user_3 = clean(request.form.get('user_3'))
        user.user_4 = clean(request.form.get('user_4'))
        user.user_5 = clean(request.form.get('user_5'))
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin_bp.admin_dashboard'))

    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/admin/users/toggle_status/<int:user_id>', methods=['POST'])
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active  # Toggle the active status
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.first_name} {user.last_name} has been {status}.', 'success')
    return redirect(url_for('admin_bp.admin_dashboard'))

