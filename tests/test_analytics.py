from datetime import date
from app.extensions import db
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale

def setup_analytics_data():
    """Seed data across consecutive months to test growth metrics."""
    c1 = Customer(customer_code="CUST-AN-1", name="Alpha Corp", region="North", segment="Enterprise")
    c2 = Customer(customer_code="CUST-AN-2", name="Beta LLC", region="South", segment="SMB")
    p1 = Product(sku="SKU-AN-1", name="Prod 1", category="Electronics", unit_cost=50.0, unit_price=100.0)
    p2 = Product(sku="SKU-AN-2", name="Prod 2", category="Software", unit_cost=20.0, unit_price=100.0)
    db.session.add_all([c1, c2, p1, p2])
    db.session.commit()

    # Month 1: 2026-01 (10 units * 100 = $1000 rev, $500 cost, $500 profit)
    s1 = Sale(
        transaction_id="TX-AN-1", customer_id=c1.id, product_id=p1.id,
        quantity=10, unit_price=100.0, unit_cost=50.0, discount=0.0,
        sale_date=date(2026, 1, 10), region="North", payment_method="Credit Card", status="Completed"
    )
    s1.calculate_totals()

    # Month 2: 2026-02 (20 units * 100 = $2000 rev, $1000 cost, $1000 profit -> positive MoM growth)
    s2 = Sale(
        transaction_id="TX-AN-2", customer_id=c2.id, product_id=p1.id,
        quantity=20, unit_price=100.0, unit_cost=50.0, discount=0.0,
        sale_date=date(2026, 2, 10), region="South", payment_method="Invoice", status="Completed"
    )
    s2.calculate_totals()

    # Month 2: another sale
    s3 = Sale(
        transaction_id="TX-AN-3", customer_id=c1.id, product_id=p2.id,
        quantity=5, unit_price=100.0, unit_cost=20.0, discount=0.10,
        sale_date=date(2026, 2, 15), region="North", payment_method="Credit Card", status="Completed"
    )
    s3.calculate_totals()

    db.session.add_all([s1, s2, s3])
    db.session.commit()


def test_executive_kpis(client, user_headers):
    """Test KPI calculations."""
    setup_analytics_data()

    res = client.get("/api/v1/analytics/summary", headers=user_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total_orders"] == 3
    assert data["total_units_sold"] == 35
    assert data["total_revenue"] > 3000
    assert data["total_profit"] > 1500
    assert data["gross_profit_margin_percent"] > 0
    assert data["average_order_value"] > 0


def test_top_products(client, user_headers):
    """Test top products ranking."""
    setup_analytics_data()

    res = client.get("/api/v1/analytics/products/top?limit=5", headers=user_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data) >= 2
    assert data[0]["total_revenue"] >= data[1]["total_revenue"]


def test_regional_breakdown(client, user_headers):
    """Test regional performance analysis."""
    setup_analytics_data()

    res = client.get("/api/v1/analytics/regions", headers=user_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    regions = [r["region"] for r in data]
    assert "North" in regions
    assert "South" in regions


def test_monthly_growth_trends(client, user_headers):
    """Test MoM calculation via Pandas."""
    setup_analytics_data()

    res = client.get("/api/v1/analytics/trends/monthly", headers=user_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data) == 2
    assert data[0]["mom_revenue_growth_percent"] == 0.0
    assert data[1]["mom_revenue_growth_percent"] > 0.0


def test_summary_statistics(client, user_headers):
    """Test NumPy/Pandas statistical distributions."""
    setup_analytics_data()

    res = client.get("/api/v1/analytics/stats", headers=user_headers)
    assert res.status_code == 200
    stats = res.get_json()["data"]
    assert stats["transaction_count"] == 3
    assert "mean" in stats["revenue"]
    assert "median" in stats["revenue"]
    assert "std_dev" in stats["revenue"]
    assert "iqr" in stats["revenue"]
