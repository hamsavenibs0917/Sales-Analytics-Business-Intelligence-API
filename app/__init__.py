import os
from flask import Flask, jsonify
from app.config import config_by_name
from app.extensions import db, jwt, cors
from app.utils.logger import setup_logger
from app.utils.error_handlers import register_error_handlers

def create_app(config_name=None):
    """
    Application Factory Pattern for Sales Analytics & BI REST API.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development").lower()

    app = Flask(__name__)
    config_obj = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_obj)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Setup structured logging
    setup_logger(app)

    # Register centralized error handlers
    register_error_handlers(app)

    # Register Blueprints
    from app.api import auth_bp, sales_bp, analytics_bp, reports_bp, customers_bp, products_bp
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(sales_bp, url_prefix="/api/v1/sales")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")
    app.register_blueprint(reports_bp, url_prefix="/api/v1/reports")
    app.register_blueprint(customers_bp, url_prefix="/api/v1/customers")
    app.register_blueprint(products_bp, url_prefix="/api/v1/products")

    # Base & Health Check routes
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "service": "Sales Analytics & Business Intelligence REST API",
            "version": "1.0.0",
            "status": "online",
            "environment": config_name,
            "documentation": "/api/v1/docs",
            "endpoints": {
                "auth": "/api/v1/auth",
                "sales": "/api/v1/sales",
                "analytics": "/api/v1/analytics",
                "reports": "/api/v1/reports",
                "customers": "/api/v1/customers",
                "products": "/api/v1/products"
            }
        }), 200

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    # CLI command to initialize database tables
    @app.cli.command("init-db")
    def init_db():
        """Initialize all database tables."""
        with app.app_context():
            db.create_all()
            print("Database tables initialized successfully.")

    return app
