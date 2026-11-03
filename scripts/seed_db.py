"""
Database Seeding Script.
Populates default users (admin, analyst, regular user), products, customers, and historical sales.
Run with: python scripts/seed_db.py
"""
import os
import sys
from datetime import date, timedelta
import random

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale

def seed_database():
    app = create_app("development")

    with app.app_context():
        print("Creating all database tables...")
        db.create_all()

        # 1. Seed Users
        users_data = [
            ("admin@company.com", "AdminPass123!", "Executive Administrator", "admin"),
            ("analyst@company.com", "AnalystPass123!", "Senior BI Analyst", "analyst"),
            ("user@company.com", "UserPass123!", "Standard Sales Rep", "user"),
        ]

        print("Seeding initial users...")
        for email, password, full_name, role in users_data:
            existing = User.query.filter_by(email=email).first()
            if not existing:
                u = User(email=email, full_name=full_name, role=role, is_active=True)
                u.set_password(password)
                db.session.add(u)
                print(f" -> Created user: {email} ({role})")

        db.session.commit()
        admin_user = User.query.filter_by(email="admin@company.com").first()

        # 2. Seed Customers
        customers_data = [
            ("CUST-1001", "Acme Corporation", "contact@acme.com", "+1-555-0101", "North", "Enterprise"),
            ("CUST-1002", "Apex Global Logistics", "billing@apexlog.com", "+1-555-0102", "South", "Enterprise"),
            ("CUST-1003", "Zenith Retail Group", "orders@zenith.com", "+1-555-0103", "East", "SMB"),
            ("CUST-1004", "Beacon Health Systems", "procurement@beacon.org", "+1-555-0104", "West", "Enterprise"),
            ("CUST-1005", "Summit Financial Partners", "info@summitfin.com", "+1-555-0105", "Central", "Enterprise"),
            ("CUST-1006", "Horizon Creative Studios", "hello@horizon.io", "+1-555-0106", "West", "SMB"),
            ("CUST-1007", "OmniTech Solutions", "sales@omnitech.com", "+1-555-0107", "North", "SMB"),
            ("CUST-1008", "Vanguard Media", "vanguard@media.com", "+1-555-0108", "East", "Consumer"),
            ("CUST-1009", "Nexus Robotics", "purchasing@nexus.ai", "+1-555-0109", "International", "Enterprise"),
            ("CUST-1010", "Starlight Cafe Franchise", "supply@starlight.com", "+1-555-0110", "Central", "Consumer"),
        ]

        print("Seeding master customers...")
        created_customers = []
        for code, name, email, phone, region, segment in customers_data:
            cust = Customer.query.filter_by(customer_code=code).first()
            if not cust:
                cust = Customer(
                    customer_code=code, name=name, email=email, phone=phone, region=region, segment=segment
                )
                db.session.add(cust)
                print(f" -> Created customer: {code} - {name}")
            created_customers.append(cust)

        db.session.commit()

        # 3. Seed Products
        products_data = [
            ("SKU-LAP-01", "ThinkPro Enterprise Laptop", "Electronics", 650.00, 1199.99),
            ("SKU-MON-02", "UltraWide 34-inch Monitor", "Electronics", 220.00, 449.99),
            ("SKU-SFT-03", "BI Cloud Analytics License (Annual)", "Software", 80.00, 499.00),
            ("SKU-SRV-04", "Dedicated Enterprise Server Node", "Electronics", 1200.00, 2499.00),
            ("SKU-CHR-05", "Ergonomic Mesh Task Chair", "Furniture", 110.00, 289.50),
            ("SKU-DSK-06", "Motorized Adjustable Standing Desk", "Furniture", 240.00, 599.00),
            ("SKU-SEC-07", "Cybersecurity Endpoint Suite", "Software", 50.00, 299.00),
            ("SKU-PRN-08", "High-Speed Laser Multi-Function Printer", "Office Supplies", 180.00, 399.99),
            ("SKU-TON-09", "High-Yield Black Toner Cartridge", "Office Supplies", 25.00, 75.00),
            ("SKU-ACC-10", "USB-C Multi-Port Docking Station", "Electronics", 35.00, 119.00),
        ]

        print("Seeding master products...")
        created_products = []
        for sku, name, category, cost, price in products_data:
            prod = Product.query.filter_by(sku=sku).first()
            if not prod:
                prod = Product(sku=sku, name=name, category=category, unit_cost=cost, unit_price=price, is_active=True)
                db.session.add(prod)
                print(f" -> Created product: {sku} - {name}")
            created_products.append(prod)

        db.session.commit()

        # 4. Seed Historical Sales (Spanning 2025 to 2026 for rich MoM & YoY growth calculations)
        if Sale.query.count() == 0:
            print("Seeding multi-year realistic sales transactions...")
            random.seed(42)

            all_custs = Customer.query.all()
            all_prods = Product.query.all()
            payment_methods = ["Credit Card", "Bank Transfer", "PayPal", "Invoice"]
            
            sales_to_insert = []
            tx_counter = 1000

            # Generate monthly sales records from 2025-01 through 2026-10
            base_date = date(2025, 1, 15)
            for month_offset in range(22):  # 22 months
                current_month_date = base_date + timedelta(days=month_offset * 30)
                # Increasing trend factor to simulate business growth
                growth_factor = 1.0 + (month_offset * 0.05)
                orders_this_month = int(random.randint(5, 10) * growth_factor)

                for _ in range(orders_this_month):
                    tx_counter += 1
                    cust = random.choice(all_custs)
                    prod = random.choice(all_prods)
                    qty = random.randint(1, 8)
                    disc = random.choice([0.0, 0.0, 0.05, 0.10, 0.15])
                    day_offset = random.randint(0, 25)
                    sale_dt = current_month_date.replace(day=min(28, current_month_date.day + day_offset % 10))

                    sale = Sale(
                        transaction_id=f"TXN-{sale_dt.year}-{tx_counter}",
                        customer_id=cust.id,
                        product_id=prod.id,
                        user_id=admin_user.id if admin_user else None,
                        quantity=qty,
                        unit_price=prod.unit_price,
                        unit_cost=prod.unit_cost,
                        discount=disc,
                        sale_date=sale_dt,
                        region=cust.region,
                        payment_method=random.choice(payment_methods),
                        status="Completed",
                    )
                    sale.calculate_totals()
                    sales_to_insert.append(sale)

            db.session.add_all(sales_to_insert)
            db.session.commit()
            print(f" -> Successfully seeded {len(sales_to_insert)} sales transactions.")
        else:
            print(f" -> Database already contains {Sale.query.count()} sales records.")

        print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
