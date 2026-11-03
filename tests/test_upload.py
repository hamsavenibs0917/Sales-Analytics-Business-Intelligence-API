import io
import pandas as pd

def test_upload_csv_dataset(client, admin_headers):
    """Test uploading a CSV dataset with auto-provisioning and deduplication."""
    csv_content = """transaction_id,customer_code,customer_name,product_sku,product_name,category,quantity,unit_price,unit_cost,discount,sale_date,region,payment_method,status
TXN-UP-001,CUST-A,Company A,SKU-A,Product A,Electronics,2,100.0,50.0,0.0,2026-06-01,North,Credit Card,Completed
TXN-UP-002,CUST-B,Company B,SKU-B,Product B,Software,5,200.0,40.0,0.10,2026-06-02,South,Invoice,Completed
TXN-UP-001,CUST-A,Company A,SKU-A,Product A,Electronics,2,100.0,50.0,0.0,2026-06-01,North,Credit Card,Completed
"""
    data = {
        "file": (io.BytesIO(csv_content.encode("utf-8")), "test_sales.csv")
    }
    res = client.post("/api/v1/sales/upload", data=data, content_type="multipart/form-data", headers=admin_headers)
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data["success"] is True
    stats = res_data["statistics"]
    assert stats["total_rows_received"] == 3
    assert stats["in_batch_duplicates_skipped"] == 1
    assert stats["inserted_records"] == 2
    assert stats["new_customers_created"] == 2
    assert stats["new_products_created"] == 2

    # Re-upload the exact same CSV to verify DB deduplication
    data2 = {
        "file": (io.BytesIO(csv_content.encode("utf-8")), "test_sales.csv")
    }
    res2 = client.post("/api/v1/sales/upload", data=data2, content_type="multipart/form-data", headers=admin_headers)
    assert res2.status_code == 200
    stats2 = res2.get_json()["statistics"]
    assert stats2["db_duplicates_skipped"] == 2
    assert stats2["inserted_records"] == 0


def test_upload_excel_dataset(client, analyst_headers):
    """Test uploading an Excel (.xlsx) dataset."""
    df = pd.DataFrame([
        {
            "transaction_id": "TXN-XL-001",
            "customer_code": "CUST-XL-1",
            "customer_name": "Excel Corp",
            "product_sku": "SKU-XL-1",
            "product_name": "Excel Widget",
            "category": "Hardware",
            "quantity": 3,
            "unit_price": 150.0,
            "unit_cost": 60.0,
            "discount": 0.05,
            "sale_date": "2026-07-01",
            "region": "West",
            "payment_method": "Credit Card",
            "status": "Completed"
        }
    ])
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    data = {
        "file": (excel_buffer, "upload_test.xlsx")
    }
    res = client.post("/api/v1/sales/upload", data=data, content_type="multipart/form-data", headers=analyst_headers)
    assert res.status_code == 200
    stats = res.get_json()["statistics"]
    assert stats["inserted_records"] == 1


def test_upload_missing_file(client, admin_headers):
    """Test upload without file raises 400."""
    res = client.post("/api/v1/sales/upload", data={}, content_type="multipart/form-data", headers=admin_headers)
    assert res.status_code == 400
    assert res.get_json()["success"] is False
