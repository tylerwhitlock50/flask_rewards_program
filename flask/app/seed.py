import argparse
from app.models import User, Retailer, PointCodes
from app.extensions import db
from app import bcrypt
from app import create_app
from datetime import datetime, timedelta
from config import ProductionConfig as Config


app = create_app(Config)

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

def seed_admin_user(retailer_id):
    """Create and return a demo admin user."""
    admin_user = User(
        email='admin@admin.com',
        username='admin_user',
        phone='555-ADMIN',
        address='Admin Lane 1',
        city='Admin City',
        state='DE',
        zip='54321',
        first_name='Admin',
        last_name='User',
        tos_agreement=True,
        tos_date=datetime.utcnow(),
        registration_date=datetime.utcnow(),
        updated_date=datetime.utcnow(),
        referal_code='ADMIN-REF',
        password_hash=bcrypt.generate_password_hash('admin').decode('utf-8'),  # Default password
        retailer_id=retailer_id,
        is_admin=True,
    )
    db.session.add(admin_user)
    db.session.commit()

def seed_multi_use_codes():
    """Create and return demo point codes."""
    codes = [
        PointCodes(
            code='WINDOW-FRONT',
            default_point_value=100,
            description='SXS Window Front Code',
            expiry_date=datetime.utcnow() + timedelta(days=365),
            updated_date=datetime.utcnow(),
            active=True,
            one_time_use=False,
            use_count=0
        ),
        PointCodes(
            code='WINDOW-REAR',
            default_point_value=75,
            description='SXS Window Rear Code',
            expiry_date=datetime.utcnow() + timedelta(days=365),
            updated_date=datetime.utcnow(),
            active=True,
            one_time_use=False,
            use_count=0
        ),
        PointCodes(
            code='OTHER',
            default_point_value=25,
            description='OTHER ITEM',
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

def create_user_from_input(retailer_id):
    """Prompt admin to enter user details via the command line and create a new user."""
    print("Enter details for the new user:")
    email = input("Email: ")
    username = input("Username: ")
    phone = input("Phone: ")
    address = input("Address: ")
    city = input("City: ")
    state = input("State: ")
    zip_code = input("Zip Code: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    password = input("Password: ")

    new_user = User(
        email=email,
        username=username,
        phone=phone,
        address=address,
        city=city,
        state=state,
        zip=zip_code,
        first_name=first_name,
        last_name=last_name,
        tos_agreement=True,
        tos_date=datetime.utcnow(),
        registration_date=datetime.utcnow(),
        updated_date=datetime.utcnow(),
        referal_code='USER-REF',
        password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
        retailer_id=retailer_id,
        is_admin=True,
    )
    db.session.add(new_user)
    db.session.commit()
    print(f"User {username} created successfully!")

def seed_data():
    """Seed the database with initial data."""
    print("Seeding retailer...")
    retailer = seed_retailer()
    print("Retailer seeded.")

    print("Seeding admin user...")
    #seed_admin_user(retailer.id)
    print("Admin user seeded.")

    print("Seeding multi-use codes...")
    seed_multi_use_codes()
    print("Multi-use codes seeded.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    with app.app_context():
        parser = argparse.ArgumentParser(description="Seed database and manage users.")
        parser.add_argument("--seed", action="store_true", help="Seed the database with demo data.")
        parser.add_argument("--add-user", action="store_true", help="Add a user interactively.")

        args = parser.parse_args()

        if args.seed:
            seed_data()
        elif args.add_user:
            retailer = Retailer.query.first()
            if retailer:
                create_user_from_input(retailer.id)
            else:
                print("No retailer found. Please seed the database first using '--seed'.")
        else:
            parser.print_help()
