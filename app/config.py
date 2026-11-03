import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig:
    """Base configuration shared across environments."""
    SECRET_KEY = os.getenv("SECRET_KEY", "sales-bi-dev-secret-key-3914a8")
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_SESSION_OPTIONS = {"expire_on_commit": False}
    
    # Normalize DATABASE_URL for SQLAlchemy 2.0 compatibility (especially on Render)
    _db_url = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'sales_bi.db')}")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sales-bi-jwt-secret-key-production-enterprise-grade-secure-2026-xyz987")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30"))
    )
    JWT_HEADER_TYPE = "Bearer"
    JWT_HEADER_NAME = "Authorization"

    # Uploads Configuration
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv("UPLOAD_FOLDER", "uploads"))
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "csv,xlsx,xls").split(","))

    # Pagination Defaults
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 20
    MAX_PER_PAGE = 100

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.path.join(BASE_DIR, os.getenv("LOG_FILE", "logs/app.log"))


class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    """Configuration for unit and integration testing with in-memory database."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)


class ProductionConfig(BaseConfig):
    """Configuration for cloud deployment (e.g., Render, AWS, Heroku)."""
    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
