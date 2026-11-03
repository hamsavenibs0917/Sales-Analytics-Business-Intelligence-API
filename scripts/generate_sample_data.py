"""
Generate standalone sample CSV and Excel datasets for testing bulk upload.
Run with: python scripts/generate_sample_data.py
"""
import os
import pandas as pd

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

rows = [
    # Normal records
    {"transaction_id": "TXN-BULK-201", "customer_code": "CUST-1001", "customer_name": "Acme Corporation", "product_sku": "SKU-LAP-01", "product_name": "ThinkPro Laptop", "category": "Electronics", "quantity": 4, "unit_price": 1199.99, "unit_cost": 650.00, "discount": 0.05, "sale_date": "2026-08-10", "region": "North", "payment_method": "Credit Card", "status": "Completed"},
    {"transaction_id": "TXN-BULK-202", "customer_code": "CUST-1002", "customer_name": "Apex Global", "product_sku": "SKU-MON-02", "product_name": "UltraWide Monitor", "category": "Electronics", "quantity": 10, "unit_price": 449.99, "unit_cost": 220.00, "discount": 0.10, "sale_date": "2026-08-12", "region": "South", "payment_method": "Bank Transfer", "status": "Completed"},
    {"transaction_id": "TXN-BULK-203", "customer_code": "CUST-1003", "customer_name": "Zenith Retail", "product_sku": "SKU-SFT-03", "product_name": "BI Cloud License", "category": "Software", "quantity": 25, "unit_price": 499.00, "unit_cost": 80.00, "discount": 0.15, "sale_date": "2026-08-15", "region": "East", "payment_method": "Invoice", "status": "Completed"},
    {"transaction_id": "TXN-BULK-204", "customer_code": "CUST-1004", "customer_name": "Beacon Health", "product_sku": "SKU-SRV-04", "product_name": "Dedicated Server", "category": "Electronics", "quantity": 2, "unit_price": 2499.00, "unit_cost": 1200.00, "discount": 0.00, "sale_date": "2026-08-18", "region": "West", "payment_method": "Credit Card", "status": "Completed"},
    {"transaction_id": "TXN-BULK-205", "customer_code": "CUST-1005", "customer_name": "Summit Financial", "product_sku": "SKU-CHR-05", "product_name": "Ergonomic Chair", "category": "Furniture", "quantity": 12, "unit_price": 289.50, "unit_cost": 110.00, "discount": 0.08, "sale_date": "2026-08-20", "region": "Central", "payment_method": "Bank Transfer", "status": "Completed"},
    # New customer and product to test auto-provisioning
    {"transaction_id": "TXN-BULK-206", "customer_code": "CUST-9999", "customer_name": "Quantum Leap AI", "product_sku": "SKU-NEW-99", "product_name": "AI Inference Accelerator", "category": "Electronics", "quantity": 5, "unit_price": 1850.00, "unit_cost": 900.00, "discount": 0.00, "sale_date": "2026-08-22", "region": "West", "payment_method": "Invoice", "status": "Completed"},
    {"transaction_id": "TXN-BULK-207", "customer_code": "CUST-1006", "customer_name": "Horizon Creative", "product_sku": "SKU-DSK-06", "product_name": "Adjustable Desk", "category": "Furniture", "quantity": 6, "unit_price": 599.00, "unit_cost": 240.00, "discount": 0.05, "sale_date": "2026-08-25", "region": "West", "payment_method": "Credit Card", "status": "Completed"},
    {"transaction_id": "TXN-BULK-208", "customer_code": "CUST-1007", "customer_name": "OmniTech", "product_sku": "SKU-SEC-07", "product_name": "Cybersecurity Suite", "category": "Software", "quantity": 15, "unit_price": 299.00, "unit_cost": 50.00, "discount": 0.10, "sale_date": "2026-08-28", "region": "North", "payment_method": "Invoice", "status": "Completed"},
    {"transaction_id": "TXN-BULK-209", "customer_code": "CUST-1008", "customer_name": "Vanguard Media", "product_sku": "SKU-ACC-10", "product_name": "USB-C Dock", "category": "Electronics", "quantity": 8, "unit_price": 119.00, "unit_cost": 35.00, "discount": 0.00, "sale_date": "2026-08-30", "region": "East", "payment_method": "PayPal", "status": "Completed"},
    {"transaction_id": "TXN-BULK-210", "customer_code": "CUST-1009", "customer_name": "Nexus Robotics", "product_sku": "SKU-PRN-08", "product_name": "Multi-Function Laser Printer", "category": "Office Supplies", "quantity": 3, "unit_price": 399.99, "unit_cost": 180.00, "discount": 0.00, "sale_date": "2026-09-02", "region": "International", "payment_method": "Bank Transfer", "status": "Completed"},
    # Duplicate transaction to test deduplication
    {"transaction_id": "TXN-BULK-201", "customer_code": "CUST-1001", "customer_name": "Acme Corporation", "product_sku": "SKU-LAP-01", "product_name": "ThinkPro Laptop", "category": "Electronics", "quantity": 4, "unit_price": 1199.99, "unit_cost": 650.00, "discount": 0.05, "sale_date": "2026-08-10", "region": "North", "payment_method": "Credit Card", "status": "Completed"},
]

df = pd.DataFrame(rows)

csv_path = os.path.join(DATA_DIR, "sample_sales.csv")
excel_path = os.path.join(DATA_DIR, "sample_sales.xlsx")

df.to_csv(csv_path, index=False)
df.to_excel(excel_path, index=False, engine="openpyxl")

print(f"Sample datasets generated successfully:")
print(f" -> CSV: {csv_path}")
print(f" -> Excel: {excel_path}")
