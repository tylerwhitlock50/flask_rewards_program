from flask import render_template, url_for
from flask_login import current_user, login_required
from app.models import User, PointsLog
from sqlalchemy import func
from datetime import datetime, timedelta
from . import dashboard_bp
from app.extensions import db

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Query top earners for the current year
    year_start = datetime(datetime.utcnow().year, 1, 1)
    top_earners_query = (
        db.session.query(
            User.username,
            func.sum(PointsLog.original_points).label('total_points')
        )
        .join(PointsLog, PointsLog.user_id == User.id)
        .filter(PointsLog.added_date >= year_start)
        .group_by(User.id)
        .order_by(func.sum(PointsLog.original_points).desc())
        .limit(5)
    )
    top_earners = [
        {"username": row.username, "total_points": row.total_points}
        for row in top_earners_query
    ]

    # User's points expiring in the next 30 days
    expiring_points = current_user.get_expiring_points(30)

    # Points earned by month for the last 12 months
    last_12_months = datetime.utcnow() - timedelta(days=365)
    points_by_month_query = (
        db.session.query(
            func.strftime('%Y-%m', PointsLog.added_date).label('month'),
            func.sum(PointsLog.original_points).label('points')
        )
        .filter(PointsLog.user_id == current_user.id, PointsLog.added_date >= last_12_months)
        .group_by('month')
        .order_by('month')
    )
    points_by_month = [{"month": row.month, "points": row.points} for row in points_by_month_query]

    # User's recent activity (last 10-50 items)
    recent_activity = (
        db.session.query(PointsLog.description, PointsLog.added_date, PointsLog.original_points)
        .filter(PointsLog.user_id == current_user.id)
        .order_by(PointsLog.added_date.desc())
        .limit(25)  # Adjust this number for more or fewer items
    ).all()

    return render_template(
        'dashboard/dashboard.html',
        user=current_user,
        top_earners=top_earners,
        expiring_points=expiring_points,
        points_by_month=points_by_month,
        recent_activity=recent_activity
    )

