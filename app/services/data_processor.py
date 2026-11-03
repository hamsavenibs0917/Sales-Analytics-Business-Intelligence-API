import io
import re
from datetime import datetime, date
import pandas as pd
import numpy as np
from flask import current_app
from app.extensions import db
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.utils.exceptions import FileProcessingError

# Column alias dictionary to support flexible CSV/Excel headers
HEADER_MAPPING = {
    "transaction_id": ["transaction_id", "transactionid", "trans_id", "order_id", "invoice_no", "invoice_id"],
    "customer_code": ["customer_code", "customercode", "customer_id", "cust_id", "client_id"],
    "customer_name": ["customer_name", "customer", "client_name", "name"],
    "product_sku": ["product_sku", "sku", "product_code", "item_code", "item_id"],
    "product_name": ["product_name", "product", "item_name", "description"],
    "category": ["category", "product_category", "item_category"],
    "quantity": ["quantity", "qty", "units", "quantity_sold"],
    "unit_price": ["unit_price", "price", "unitprice", "rate"],
    "unit_cost": ["unit_cost", "cost", "unitcost", "cost_price"],
    "discount": ["discount", "disc", "discount_rate", "discount_percent"],
    "sale_date": ["sale_date", "date", "order_date", "transaction_date"],
    "region": ["region", "sales_region", "territory", "area"],
    "payment_method": ["payment_method", "payment_type", "payment"],
    "status": ["status", "order_status", "sale_status"],
}

class DataProcessor:
    """ETL, Data Cleaning, Deduplication, and Ingestion Engine using Pandas & NumPy."""

    @staticmethod
    def read_file_to_dataframe(file_storage) -> pd.DataFrame:
        """Read CSV or Excel FileStorage object into a pandas DataFrame."""
        filename = file_storage.filename.lower()
        content = file_storage.read()

        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(content))
            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(io.BytesIO(content))
            else:
                raise FileProcessingError("Unsupported file format. Please upload a .csv, .xlsx, or .xls file.")
        except Exception as e:
            raise FileProcessingError(f"Error parsing file: {str(e)}")

        if df.empty:
            raise FileProcessingError("The uploaded file contains no data rows.")

        return df

    @classmethod
    def normalize_column_headers(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Map heterogeneous column names to standard canonical attributes."""
        raw_cols = {col: str(col).strip().lower().replace(" ", "_").replace("-", "_") for col in df.columns}
        df = df.rename(columns=raw_cols)

        rename_map = {}
        for canonical, aliases in HEADER_MAPPING.items():
            for col in df.columns:
                if col in aliases:
                    rename_map[col] = canonical
                    break

        return df.rename(columns=rename_map)

    @classmethod
    def clean_and_validate(cls, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """
        Cleans data types, parses dates, validates numeric bounds, and detects duplicates.
        Returns: (cleaned_df, processing_stats)
        """
        stats = {
            "total_rows_received": len(df),
            "invalid_rows_dropped": 0,
            "in_batch_duplicates_skipped": 0,
            "db_duplicates_skipped": 0,
            "valid_records_to_insert": 0,
        }

        df = cls.normalize_column_headers(df)

        required_cols = ["transaction_id", "customer_code", "product_sku", "quantity", "unit_price", "sale_date"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise FileProcessingError(
                f"Missing mandatory columns: {missing_cols}. Found columns: {list(df.columns)}"
            )

        # 1. Clean Transaction ID and strip strings
        df["transaction_id"] = df["transaction_id"].astype(str).str.strip()
        df["customer_code"] = df["customer_code"].astype(str).str.strip()
        df["product_sku"] = df["product_sku"].astype(str).str.strip()

        # Drop null/empty mandatory fields
        before_drop = len(df)
        df = df.dropna(subset=required_cols)
        df = df[(df["transaction_id"] != "") & (df["customer_code"] != "") & (df["product_sku"] != "")]
        stats["invalid_rows_dropped"] += (before_drop - len(df))

        # 2. In-batch Deduplication
        before_dedup = len(df)
        df = df.drop_duplicates(subset=["transaction_id"], keep="first")
        stats["in_batch_duplicates_skipped"] = before_dedup - len(df)

        # 3. Numeric Conversions & Validations
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
        
        # Unit Cost (defaults to 70% of unit price if unspecified)
        if "unit_cost" in df.columns:
            df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce").fillna(df["unit_price"] * 0.7)
        else:
            df["unit_cost"] = df["unit_price"] * 0.7

        # Discount (normalizes percentage 10 -> 0.10 or maintains decimal 0.10)
        if "discount" in df.columns:
            df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0.0)
            # If discount is > 1.0 (e.g. 15 for 15%), convert to decimal
            df["discount"] = np.where(df["discount"] > 1.0, df["discount"] / 100.0, df["discount"])
            df["discount"] = df["discount"].clip(lower=0.0, upper=1.0)
        else:
            df["discount"] = 0.0

        # Drop invalid numeric records (quantity <= 0 or price <= 0)
        valid_numeric = (df["quantity"] > 0) & (df["unit_price"] > 0) & (df["unit_cost"] >= 0)
        invalid_nums = (~valid_numeric).sum()
        stats["invalid_rows_dropped"] += int(invalid_nums)
        df = df[valid_numeric]

        df["quantity"] = df["quantity"].astype(int)

        # 4. Date Parsing
        df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
        invalid_dates = df["sale_date"].isna().sum()
        stats["invalid_rows_dropped"] += int(invalid_dates)
        df = df.dropna(subset=["sale_date"])
        df["sale_date"] = df["sale_date"].dt.date

        # 5. Categorical normalization
        if "region" not in df.columns or df["region"].isna().all():
            df["region"] = "Central"
        else:
            df["region"] = df["region"].fillna("Central").astype(str).str.strip().str.title()

        if "payment_method" not in df.columns:
            df["payment_method"] = "Credit Card"
        else:
            df["payment_method"] = df["payment_method"].fillna("Credit Card").astype(str).str.strip()

        if "status" not in df.columns:
            df["status"] = "Completed"
        else:
            df["status"] = df["status"].fillna("Completed").astype(str).str.strip().str.title()

        # 6. Database Deduplication Check
        existing_tx_ids = set(
            row[0] for row in db.session.query(Sale.transaction_id).filter(
                Sale.transaction_id.in_(df["transaction_id"].tolist())
            ).all()
        )
        stats["db_duplicates_skipped"] = len(existing_tx_ids)
        if existing_tx_ids:
            df = df[~df["transaction_id"].isin(existing_tx_ids)]

        stats["valid_records_to_insert"] = len(df)
        return df, stats

    @classmethod
    def ingest_sales_dataframe(cls, df: pd.DataFrame, stats: dict, user_id=None) -> dict:
        """
        Upserts referenced Customers and Products, then bulk-inserts cleaned Sale records.
        """
        if df.empty:
            stats["inserted_records"] = 0
            return stats

        # 1. Resolve and create missing Customers
        unique_customers = df[["customer_code", "region"]].drop_duplicates(subset=["customer_code"])
        cust_name_col = "customer_name" if "customer_name" in df.columns else None

        existing_customers = {
            c.customer_code: c for c in Customer.query.filter(
                Customer.customer_code.in_(unique_customers["customer_code"].tolist())
            ).all()
        }

        new_customers = []
        for _, row in unique_customers.iterrows():
            code = row["customer_code"]
            if code not in existing_customers:
                name = str(row[cust_name_col]) if cust_name_col and pd.notna(row.get(cust_name_col)) else f"Customer {code}"
                new_cust = Customer(
                    customer_code=code,
                    name=name,
                    region=row["region"] if pd.notna(row["region"]) else "Central",
                    segment="Consumer"
                )
                new_customers.append(new_cust)

        if new_customers:
            db.session.add_all(new_customers)
            db.session.flush()
            for c in new_customers:
                existing_customers[c.customer_code] = c

        stats["new_customers_created"] = len(new_customers)

        # 2. Resolve and create missing Products
        unique_products = df[["product_sku", "unit_cost", "unit_price"]].drop_duplicates(subset=["product_sku"])
        prod_name_col = "product_name" if "product_name" in df.columns else None
        prod_cat_col = "category" if "category" in df.columns else None

        existing_products = {
            p.sku: p for p in Product.query.filter(
                Product.sku.in_(unique_products["product_sku"].tolist())
            ).all()
        }

        new_products = []
        for _, row in unique_products.iterrows():
            sku = row["product_sku"]
            if sku not in existing_products:
                name = str(row[prod_name_col]) if prod_name_col and pd.notna(row.get(prod_name_col)) else f"Product {sku}"
                cat = str(row[prod_cat_col]) if prod_cat_col and pd.notna(row.get(prod_cat_col)) else "General"
                new_prod = Product(
                    sku=sku,
                    name=name,
                    category=cat,
                    unit_cost=float(row["unit_cost"]),
                    unit_price=float(row["unit_price"]),
                    is_active=True
                )
                new_products.append(new_prod)

        if new_products:
            db.session.add_all(new_products)
            db.session.flush()
            for p in new_products:
                existing_products[p.sku] = p

        stats["new_products_created"] = len(new_products)

        # 3. Create Sale records
        sale_objects = []
        for _, row in df.iterrows():
            qty = int(row["quantity"])
            price = float(row["unit_price"])
            cost = float(row["unit_cost"])
            disc = float(row["discount"])
            gross = qty * price
            revenue = round(gross * (1.0 - disc), 2)
            total_cost = round(qty * cost, 2)
            profit = round(revenue - total_cost, 2)

            cust = existing_customers[row["customer_code"]]
            prod = existing_products[row["product_sku"]]

            sale = Sale(
                transaction_id=str(row["transaction_id"]),
                customer_id=cust.id,
                product_id=prod.id,
                user_id=user_id,
                quantity=qty,
                unit_price=price,
                unit_cost=cost,
                discount=disc,
                total_revenue=revenue,
                total_cost=total_cost,
                total_profit=profit,
                sale_date=row["sale_date"],
                region=str(row["region"]),
                payment_method=str(row["payment_method"]),
                status=str(row["status"]),
            )
            sale_objects.append(sale)

        db.session.add_all(sale_objects)
        db.session.commit()

        stats["inserted_records"] = len(sale_objects)
        return stats

    @staticmethod
    def compute_summary_statistics(sales_query) -> dict:
        """
        Extract summary statistics on sales transactions using Pandas and NumPy.
        """
        rows = sales_query.with_entities(
            Sale.total_revenue, Sale.total_profit, Sale.quantity, Sale.discount
        ).all()

        if not rows:
            return {
                "transaction_count": 0,
                "revenue": {"mean": 0.0, "median": 0.0, "std_dev": 0.0, "min": 0.0, "max": 0.0, "q25": 0.0, "q75": 0.0, "iqr": 0.0},
                "profit": {"mean": 0.0, "median": 0.0, "std_dev": 0.0, "min": 0.0, "max": 0.0},
                "quantity": {"mean": 0.0, "median": 0.0, "total": 0},
            }

        df = pd.DataFrame(rows, columns=["revenue", "profit", "quantity", "discount"])

        rev_q25 = float(np.percentile(df["revenue"], 25))
        rev_q75 = float(np.percentile(df["revenue"], 75))

        return {
            "transaction_count": int(len(df)),
            "revenue": {
                "mean": round(float(df["revenue"].mean()), 2),
                "median": round(float(df["revenue"].median()), 2),
                "std_dev": round(float(df["revenue"].std(ddof=0)), 2),
                "min": round(float(df["revenue"].min()), 2),
                "max": round(float(df["revenue"].max()), 2),
                "q25": round(rev_q25, 2),
                "q75": round(rev_q75, 2),
                "iqr": round(rev_q75 - rev_q25, 2),
            },
            "profit": {
                "mean": round(float(df["profit"].mean()), 2),
                "median": round(float(df["profit"].median()), 2),
                "std_dev": round(float(df["profit"].std(ddof=0)), 2),
                "min": round(float(df["profit"].min()), 2),
                "max": round(float(df["profit"].max()), 2),
            },
            "quantity": {
                "mean": round(float(df["quantity"].mean()), 2),
                "median": round(float(df["quantity"].median()), 2),
                "total": int(df["quantity"].sum()),
            },
        }
