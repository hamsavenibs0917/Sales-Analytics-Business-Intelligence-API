from app.api.auth import auth_bp
from app.api.sales import sales_bp
from app.api.analytics import analytics_bp
from app.api.reports import reports_bp
from app.api.customers import customers_bp
from app.api.products import products_bp

__all__ = [
    "auth_bp",
    "sales_bp",
    "analytics_bp",
    "reports_bp",
    "customers_bp",
    "products_bp",
]
