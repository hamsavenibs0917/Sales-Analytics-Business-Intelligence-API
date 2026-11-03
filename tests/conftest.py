import os
import sys

# Ensure root workspace directory is on sys.path for test discovery
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask_jwt_extended import create_access_token
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.customer import Customer
from app.models.product import Product

@pytest.fixture(scope="session")
def app():
    """Create and configure a clean Flask app for testing."""
    os.environ["FLASK_ENV"] = "testing"
    app = create_app("testing")
    return app


@pytest.fixture(scope="function")
def app_ctx(app):
    """Provide an isolated application and database context per test function."""
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    yield ctx
    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture(scope="function")
def client(app, app_ctx):
    """A test client for the app."""
    return app.test_client()


class MockUser:
    """Lightweight user record to avoid detached session issues across fixtures."""
    def __init__(self, user_id, email, full_name, role):
        self.id = user_id
        self.email = email
        self.full_name = full_name
        self.role = role


@pytest.fixture
def admin_user(app_ctx):
    """Seed an admin user."""
    user = User(email="test_admin@company.com", full_name="Test Admin", role="admin", is_active=True)
    user.set_password("AdminPass123!")
    db.session.add(user)
    db.session.commit()
    return MockUser(user.id, user.email, user.full_name, user.role)


@pytest.fixture
def analyst_user(app_ctx):
    """Seed an analyst user."""
    user = User(email="test_analyst@company.com", full_name="Test Analyst", role="analyst", is_active=True)
    user.set_password("AnalystPass123!")
    db.session.add(user)
    db.session.commit()
    return MockUser(user.id, user.email, user.full_name, user.role)


@pytest.fixture
def regular_user(app_ctx):
    """Seed a regular user."""
    user = User(email="test_user@company.com", full_name="Test User", role="user", is_active=True)
    user.set_password("UserPass123!")
    db.session.add(user)
    db.session.commit()
    return MockUser(user.id, user.email, user.full_name, user.role)


@pytest.fixture
def admin_headers(app_ctx, admin_user):
    """Bearer authorization headers for Admin."""
    claims = {"role": "admin", "email": admin_user.email}
    token = create_access_token(identity=str(admin_user.id), additional_claims=claims)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def analyst_headers(app_ctx, analyst_user):
    """Bearer authorization headers for Analyst."""
    claims = {"role": "analyst", "email": analyst_user.email}
    token = create_access_token(identity=str(analyst_user.id), additional_claims=claims)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers(app_ctx, regular_user):
    """Bearer authorization headers for Regular User."""
    claims = {"role": "user", "email": regular_user.email}
    token = create_access_token(identity=str(regular_user.id), additional_claims=claims)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_catalog(app_ctx):
    """Seed sample customer and product."""
    cust = Customer(
        customer_code="CUST-TEST-1",
        name="Test Customer Inc",
        email="test@customer.com",
        region="North",
        segment="Enterprise"
    )
    prod = Product(
        sku="SKU-TEST-1",
        name="Test Widget",
        category="Hardware",
        unit_cost=50.00,
        unit_price=100.00,
        is_active=True
    )
    db.session.add_all([cust, prod])
    db.session.commit()

    return {
        "customer_id": cust.id,
        "product_id": prod.id,
        "customer_code": cust.customer_code,
        "product_sku": prod.sku,
    }
