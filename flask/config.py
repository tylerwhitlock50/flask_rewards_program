import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Replace with a secure key in production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')  # Default to SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable event system to save resources
    DEBUG = True  # Enable debug mode for development
    RECEIPT_UPLOAD_FOLDER = 'app/static/receipts'  # Folder for uploaded receipts
    VISA_VALUE = 1
    GIFT_CARD_VALUE = 1.25
    MINIMUM_REDEMPTION = 50
    SECRET_KEY = os.getenv('SECRET_KEY', 'default')

    MAIL_SERVER = 'smtp-mail.outlook.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
        

class DevelopmentConfig(Config):
    ENV = 'development'

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False  # Disable debug mode in production
    SQLALCHEMY_DATABASE_URI = os.getenv('PROD_DATABASE_URL')  # Use PostgreSQL in production

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite for tests
