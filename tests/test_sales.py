import json

def test_create_sale(client, admin_headers, sample_catalog):
    """Test creating a sales transaction with automated revenue and profit calculation."""
    payload = {
        "transaction_id": "TXN-TEST-100",
        "customer_id": sample_catalog["customer_id"],
        "product_id": sample_catalog["product_id"],
        "quantity": 5,
        "unit_price": 100.0,
        "unit_cost": 50.0,
        "discount": 0.10,  # 10% discount
        "sale_date": "2026-05-15",
        "region": "North",
        "payment_method": "Credit Card",
        "status": "Completed"
    }
    res = client.post("/api/v1/sales", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    sale = data["sale"]
    assert sale["total_revenue"] == 450.0  # 5 * 100 * 0.90
    assert sale["total_cost"] == 250.0     # 5 * 50
    assert sale["total_profit"] == 200.0   # 450 - 250
    assert sale["profit_margin_percent"] == 44.44


def test_get_sale_by_id(client, admin_headers, sample_catalog):
    """Test retrieving a sales record by ID."""
    # Create sale first
    payload = {
        "transaction_id": "TXN-TEST-101",
        "customer_id": sample_catalog["customer_id"],
        "product_id": sample_catalog["product_id"],
        "quantity": 2,
        "unit_price": 100.0,
        "sale_date": "2026-05-16",
        "region": "North"
    }
    create_res = client.post("/api/v1/sales", json=payload, headers=admin_headers)
    sale_id = create_res.get_json()["sale"]["id"]

    res = client.get(f"/api/v1/sales/{sale_id}", headers=admin_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["sale"]["transaction_id"] == "TXN-TEST-101"
    assert data["sale"]["customer"]["customer_code"] == sample_catalog["customer_code"]


def test_update_sale(client, admin_headers, sample_catalog):
    """Test updating sales record recalculates profit metrics."""
    payload = {
        "transaction_id": "TXN-TEST-102",
        "customer_id": sample_catalog["customer_id"],
        "product_id": sample_catalog["product_id"],
        "quantity": 1,
        "unit_price": 100.0,
        "unit_cost": 50.0,
        "discount": 0.0,
        "sale_date": "2026-05-17",
        "region": "North"
    }
    create_res = client.post("/api/v1/sales", json=payload, headers=admin_headers)
    sale_id = create_res.get_json()["sale"]["id"]

    # Update quantity from 1 to 10
    update_res = client.put(f"/api/v1/sales/{sale_id}", json={"quantity": 10}, headers=admin_headers)
    assert update_res.status_code == 200
    updated = update_res.get_json()["sale"]
    assert updated["quantity"] == 10
    assert updated["total_revenue"] == 1000.0
    assert updated["total_profit"] == 500.0


def test_delete_sale_rbac(client, admin_headers, user_headers, sample_catalog):
    """Test deletion requires admin role and blocks regular user with 403."""
    payload = {
        "transaction_id": "TXN-TEST-103",
        "customer_id": sample_catalog["customer_id"],
        "product_id": sample_catalog["product_id"],
        "quantity": 1,
        "unit_price": 100.0,
        "sale_date": "2026-05-18",
        "region": "North"
    }
    create_res = client.post("/api/v1/sales", json=payload, headers=admin_headers)
    sale_id = create_res.get_json()["sale"]["id"]

    # Try deleting with regular user -> should fail with 403 Forbidden
    forbidden_res = client.delete(f"/api/v1/sales/{sale_id}", headers=user_headers)
    assert forbidden_res.status_code == 403

    # Delete with admin -> should succeed 200
    success_res = client.delete(f"/api/v1/sales/{sale_id}", headers=admin_headers)
    assert success_res.status_code == 200
