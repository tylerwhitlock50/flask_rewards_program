from app.models import User, Retailer, PointsLog, PointCodes, RedemptionLog
from app.extensions import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def seed_retailer():
    """Create and return a demo retailer."""
    retailer = Retailer(
        name='Demo Retailer',
        address='456 Demo Street',
        phone='987-654-3210',
        updated_date=datetime.utcnow(),
        responsible_user='Demo Admin',
        salesep_id='123',
        territory_id='45',
        customer_group='Group A',
        team_id='Team Alpha',
        retailer_1='DemoField1',
    )
    db.session.add(retailer)
    db.session.commit()
    return retailer

def seed_users(retailer_id):
    """Create and return demo users associated with the given retailer."""
    users = [
        User(
            email=f'user{i}@demo.com',
            username=f'demo_user{i}',
            phone=f'555-000-{i:04}',
            address=f'{i} Demo Lane',
            first_name='Demo',
            last_name=f'User {i}',
            tos_agreement=True,
            tos_date=datetime.utcnow(),
            registration_date=datetime.utcnow(),
            updated_date=datetime.utcnow(),
            referal_code=f'REF-{i}',
            password_hash=generate_password_hash('password'),
            retailer_id=retailer_id,
        )
        for i in range(1, 6)
    ]
    db.session.bulk_save_objects(users)
    db.session.commit()

    # Re-query users to get IDs
    return User.query.filter(User.retailer_id == retailer_id).all()

def seed_point_codes():
    """Create and return demo point codes."""
    codes = [
        PointCodes(
            code=f'CODE-{i}',
            default_point_value=500 + (100 * i),
            description=f'Demo Code {i}',
            expiry_date=datetime.utcnow() + timedelta(days=30),
            updated_date=datetime.utcnow(),
            active=True,
            one_time_use=True,
            use_count=0
        )
        for i in range(1, 6)
    ]
    db.session.add_all(codes)
    db.session.commit()
    return codes

def seed_additional_point_codes():
    """Create and return demo point codes."""
    codes = [
        PointCodes(
            code=f'CODE-{i}',
            default_point_value=500 + (100 * i),
            description=f'Demo Code {i}',
            expiry_date=datetime.utcnow() + timedelta(days=30),
            updated_date=datetime.utcnow(),
            active=True,
            one_time_use=True,
            use_count=0
        )
        for i in range(10, 100)
    ]
    db.session.add_all(codes)
    db.session.commit()
    return codes

def seed_multi_use_codes():
    """Create and return demo point codes."""
    codes = [
        PointCodes(
            code=f'WINDOW-FRONT',
            default_point_value=100,
            description=f'SXS Window Front Code',
            expiry_date=datetime.utcnow() + timedelta(days=365),
            updated_date=datetime.utcnow(),
            active=True,
            one_time_use=False,
            use_count=0
            
        ),
        PointCodes(
            code=f'WINDOW-REAR',
            default_point_value=75,
            description=f'SXS Window Rear Code',
            expiry_date=datetime.utcnow() + timedelta(days=365),
            updated_date=datetime.utcnow(),
            active=True,
            one_time_use=False,
            use_count=0
        ),
        PointCodes(
            code=f'OTHER',
            default_point_value=25,
            description=f'OTHER ITEM',
            expiry_date=datetime.utcnow() + timedelta(days=365),
            updated_date=datetime.utcnow(),
            active=True,
            one_time_use=False,
            use_count=0
        )
        
    ]
    db.session.add_all(codes)
    db.session.commit()
    return codes

def seed_points_logs(users, codes):
    """Create points logs for demo users using point codes."""
    for user, code in zip(users, codes):
        log = PointsLog(
            user_id=user.id,
            points=code.default_point_value,
            original_points=code.default_point_value,
            description=f"Points from {code.code}",
            added_date=datetime.utcnow(),
            expiry_date=code.expiry_date,
            code_used=code.id,
            approved = True,
            approved_by = 'DEMO'
        )
        code.consume_code()
        db.session.add(log)
    db.session.commit()

def seed_redemptions(users):
    """Create redemptions for demo users."""
    for user in users[:3]:  # Redeem points for first 3 users
        # redemption = RedemptionLog(
        #     user_id=user.id,
        #     points=500,
        #     description="Redeemed for Demo Reward",
        #     redemption_date=datetime.utcnow(),
        # )
        user.redeem_points(500, "credit")
        #db.session.add(redemption)
    db.session.commit()

def seed_admin_user(retailer_id):
    """Create and return a demo admin user."""
    admin_user = User(
        email='admin@admin.com',
        username='admin_user',
        phone='555-ADMIN',
        address='Admin Lane 1',
        first_name='Admin',
        last_name='User',
        tos_agreement=True,
        tos_date=datetime.utcnow(),
        registration_date=datetime.utcnow(),
        updated_date=datetime.utcnow(),
        referal_code='ADMIN-REF',
        password_hash=generate_password_hash('admin'),  # Default password
        retailer_id=retailer_id,
        is_admin=True,
    )
    db.session.add(admin_user)
    db.session.commit()
    

def seed_demo_data():
    """Seed the entire database with demo data."""
    retailer = seed_retailer()
    users = seed_users(retailer.id)

    # Verify user IDs
    for user in users:
        assert user.id, f"User {user.username} does not have a valid ID."

    codes = seed_point_codes()

    # Verify code IDs
    for code in codes:
        assert code.id, f"Code {code.code} does not have a valid ID."

    seed_points_logs(users, codes)
    seed_redemptions(users)
    print("Demo data seeded successfully.")
    seed_additional_point_codes()
    seed_multi_use_codes()
    seed_admin_user(retailer.id)