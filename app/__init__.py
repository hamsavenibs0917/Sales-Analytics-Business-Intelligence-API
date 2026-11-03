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
        from flask import render_template, request
        # If user visits in a web browser, serve the interactive BI Dashboard
        accept_header = request.headers.get("Accept", "")
        if "text/html" in accept_header:
            return render_template("dashboard.html")

        return jsonify({
            "service": "Sales Analytics & Business Intelligence REST API",
            "version": "1.0.0",
            "status": "online",
            "environment": config_name,
            "dashboard": "/dashboard",
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

    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        """Direct website route for the Business Intelligence Dashboard."""
        from flask import render_template
        return render_template("dashboard.html")

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    @app.route("/api/v1/seed", methods=["GET", "POST"])
    def trigger_seed():
        """Public endpoint to seed or restore database with demo dataset."""
        from scripts.seed_db import seed_database
        try:
            seed_database(app)
            return jsonify({
                "success": True,
                "message": "Database successfully populated with default users, catalog, and historical sales transactions."
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route("/api/v1/openapi.json", methods=["GET"])
    def openapi_spec():
        """Serve the OpenAPI 3.0 specification."""
        from flask import Response
        spec_path = os.path.join(os.path.dirname(app.root_path), "docs", "openapi.json")
        if not os.path.exists(spec_path):
            # Fallback to local app path if packaged
            spec_path = os.path.join(app.root_path, "docs", "openapi.json")
        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                return Response(f.read(), mimetype="application/json")
        except Exception:
            return jsonify({"error": "OpenAPI specification file not found."}), 404

    @app.route("/api/v1/docs", methods=["GET"])
    def swagger_ui():
        """Serve interactive Swagger UI documentation dashboard."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Sales Analytics & BI REST API - Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
    <style>
        body { margin: 0; background: #fafafa; }
        .swagger-ui .topbar { background-color: #1e3a8a; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js" crossorigin></script>
    <script>
        window.onload = () => {
            window.ui = SwaggerUIBundle({
                url: '/api/v1/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [SwaggerUIBundle.presets.apis],
            });
        };
    </script>
</body>
</html>"""

    # CLI command to initialize database tables
    @app.cli.command("init-db")
    def init_db():
        """Initialize all database tables."""
        with app.app_context():
            db.create_all()
            print("Database tables initialized successfully.")

    return app
