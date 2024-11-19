from flask import current_app
from flask_login import UserMixin
from app.extensions import db
from datetime import datetime, timedelta


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    tos_agreement = db.Column(db.Boolean, nullable=False)
    tos_date = db.Column(db.DateTime, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False)
    updated_date = db.Column(db.DateTime, nullable=False)
    referal_code = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'), nullable=False)
    points_logs = db.relationship('PointsLog', backref='user', lazy=True)
    redemption_logs = db.relationship('RedemptionLog', backref='user', lazy=True)

    #Roles and permissions
    is_admin = db.Column(db.Boolean, default=False)
    is_sales_manager = db.Column(db.Boolean, default=False)
    is_customer_service = db.Column(db.Boolean, default=False)
    is_internal = db.Column(db.Boolean, default=False)

    # Custom fields for user fo promos and later classifcation
    salesep_id = db.Column(db.String(30), nullable=True)
    territory_id = db.Column(db.String(30), nullable=True)
    customer_group = db.Column(db.String(30), nullable=True)
    team_id = db.Column(db.String(30), nullable=True)
    user_1 = db.Column(db.String(30), nullable=True)
    user_2 = db.Column(db.String(30), nullable=True)
    user_3 = db.Column(db.String(30), nullable=True)
    user_4 = db.Column(db.String(30), nullable=True)
    user_5 = db.Column(db.String(30), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_point_balance(self):
        """Calculate the user's current point balance."""
        earned_points = sum(
            log.original_points for log in self.points_logs if not log.is_expired()
        )
        redeemed_points = sum(
            redemption.points for redemption in self.redemption_logs
        )
        return earned_points - redeemed_points
    
    def get_expiring_points(self, days):
        """Get points that will expire in the next 'x' days."""
        upcoming_expiry_date = datetime.utcnow() + timedelta(days=days)
        
        expiring_points_logs = [
            log for log in self.points_logs 
            if log.expiry_date and datetime.utcnow() < log.expiry_date <= upcoming_expiry_date
        ]

        expiring_points = sum(log.points for log in expiring_points_logs)

        return {
            "expiring_points": expiring_points,
            "details": expiring_points_logs
        }
    
    def log_points(self, code_str, file_reference=None):
        """Log points for the user using a pre-approved code."""
        # Validate the code
        code = PointCodes.query.filter_by(code=code_str).first()
        if not code or not code.is_valid():
            raise ValueError("Invalid or expired code.")
        
        # Log points and associate it with the code
        points_log = PointsLog(
            user_id=self.id,
            points=code.default_point_value,
            original_points=code.default_point_value,
            description=code.description,
            added_date=datetime.utcnow(),
            expiry_date=code.expiry_date,
            code_used=code.id,
            file_reference=file_reference
        )
        code.consume_code()  # Mark as used
        db.session.add(points_log)
        db.session.commit()
        return points_log
    
    def has_unapproved_receipts(self):
        """Check if the user has any unapproved receipt submissions."""
        for log in self.points_logs:
            # Assuming logs that are not rejected or approved are pending
            if log.approved == True:
                continue  # Skip rejected logs
            if not log.points or log.points == 0:
                continue  # Skip logs where points were denied
            # Add any additional logic if there's a specific approved flag
            return True
        return False
    
    def redeem_points(self, amount, redemption_type):
        """Redeem points by using the oldest unexpired points."""

        if self.has_unapproved_receipts():
            raise ValueError("Cannot redeem points. Unapproved receipts are pending.")
        if amount <= 0:
            raise ValueError("Redemption amount must be positive.")

        if amount > self.get_point_balance():
            raise ValueError("Not enough points to redeem.")
        
        if amount < current_app.config['MINIMUM_REDEMPTION']:
            raise ValueError(f"Minimum redemption is {current_app.config['MINIMUM_REDEMPTION']} points.")

        # Determine the cash value and description based on the redemption type
        if redemption_type == 'credit':
            cash_value = amount * current_app.config['GIFT_CARD_VALUE']  # Supercomp Gift Card value
            description = f'Supercomp Gift Card worth ${cash_value:.2f}'
        elif redemption_type == 'visa':
            cash_value = amount * current_app.config['VISA_VALUE']  # VISA Gift Card value
            description = f'VISA Gift Card worth ${cash_value:.2f}'
        else:
            raise ValueError("Invalid redemption type.")

        # Deduct points from oldest logs first
        unexpired_logs = sorted(
            [log for log in self.points_logs if not log.is_expired() and log.points > 0],
            key=lambda log: log.expiry_date or datetime.max
        )

        points_to_redeem = amount
        for log in unexpired_logs:
            if points_to_redeem <= 0:
                break

            if log.points >= points_to_redeem:
                log.points -= points_to_redeem
                points_to_redeem = 0
            else:
                points_to_redeem -= log.points
                log.points = 0

        # Create redemption log with cash value in the description
        redemption_log = RedemptionLog(
            user_id=self.id,
            points=amount,
            description=description,
            redemption_date=datetime.utcnow()
        )
        db.session.add(redemption_log)
        db.session.commit()
        return redemption_log


class Retailer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    updated_date = db.Column(db.DateTime, nullable=False)
    responsible_user = db.Column(db.String(30), nullable=False)
    users = db.relationship('User', backref='retailer', lazy=True)

    # Custom fields for retailer for promos and later classifcation
    salesep_id = db.Column(db.String(30), nullable=True)
    territory_id = db.Column(db.String(30), nullable=True)
    customer_group = db.Column(db.String(30), nullable=True)
    team_id = db.Column(db.String(30), nullable=True)
    retailer_1 = db.Column(db.String(30), nullable=True)
    retailer_2 = db.Column(db.String(30), nullable=True)
    retailer_3 = db.Column(db.String(30), nullable=True)
    retailer_4 = db.Column(db.String(30), nullable=True)
    retailer_5 = db.Column(db.String(30), nullable=True)

    def get_store_users(self):
        return User.query.filter_by(retailer_id=self.id).all()
    
    def get_store_points(self):
        return sum(user.get_point_balance() for user in self.get_store_users())
    
    def get_store_redemptions(self):
        return sum(user.redemption_logs for user in self.get_store_users())

class PointsLog(db.Model):
    # Retains `original_points` for history.
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    original_points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=True)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True, nullable=False)
    
    code_used = db.Column(db.Integer, db.ForeignKey('point_codes.id'), nullable=False)
    
    code = db.relationship('PointCodes', back_populates='points_logs', lazy=True)
    file_reference = db.Column(db.String(100), nullable=True)
    approved = db.Column(db.Boolean, default=False, nullable=False)
    approved_by = db.Column(db.String(30), nullable=True)

    def is_expired(self):
        return self.expiry_date and self.expiry_date <= datetime.utcnow()
    

class RedemptionLog(db.Model):
    # Tracks redemptions
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    redemption_date = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    gift_card_sent = db.Column(db.Boolean, default=False, nullable=False)
    

    def __repr__(self):
        return f"<RedemptionLog User {self.user_id}: -{self.points} points for {self.description}>"
    
    def mark_sent(self):
        self.gift_card_sent = True
        db.session.commit()
    
class PointCodes(db.Model):
    # Code activation, one-time use, or reusable logic
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    default_point_value = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=True)
    updated_date = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    one_time_use = db.Column(db.Boolean, nullable=False, default=True)
    use_count = db.Column(db.Integer, nullable=False, default=0)
    points_logs = db.relationship('PointsLog', back_populates='code', lazy=True)

    def is_valid(self):
        """Check if code is still valid."""
        if not self.active or (self.expiry_date and self.expiry_date <= datetime.utcnow()):
            return False
        if self.one_time_use and self.use_count > 0:
            return False
        return True
    
    def consume_code(self):
        """Consume code during logging. Deactivate if one-time."""
        self.use_count += 1
        if self.one_time_use:
            self.active = False
        db.session.commit()
