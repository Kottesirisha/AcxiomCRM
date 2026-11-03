import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Use MySQL DATABASE_URL if configured, otherwise fallback to SQLite for local development/testing when MySQL server is not active
    default_db = 'mysql+pymysql://root:password@localhost/acxiomcrm'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', default_db)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configure engine options conditionally
    if 'sqlite' not in SQLALCHEMY_DATABASE_URI.lower():
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_recycle': 280,
            'pool_pre_ping': True,
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {}

    WTF_CSRF_ENABLED = True
    ITEMS_PER_PAGE = 15
