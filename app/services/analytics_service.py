from datetime import datetime, date
import pandas as pd
import numpy as np
from sqlalchemy import func, extract, desc, asc
from app.extensions import db
from app.models.sale import Sale
from app.models.product import Product
from app.models.customer import Customer

class AnalyticsService:
    """Core BI analytics engine computing SQL aggregates and Pandas/NumPy time-series metrics."""

    @classmethod
    def apply_sales_filters(cls, query, start_date=None, end_date=None, region=None, status=None):
        """Helper to apply common query filters."""
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Sale.sale_date <= end_date)
        if region:
            query = query.filter(func.lower(Sale.region) == region.lower())
        if status:
            query = query.filter(Sale.status == status)
        else:
            # By default exclude cancelled and refunded for revenue analysis
            query = query.filter(~Sale.status.in_(["Cancelled", "Refunded"]))
        return query

    @classmethod
    def get_summary_kpis(cls, start_date=None, end_date=None, region=None) -> dict:
        """
        Calculates executive KPIs: Total Revenue, Profit, Cost, Margin %, Units, Orders, AOV.
        """
        query = db.session.query(
            func.coalesce(func.sum(Sale.total_revenue), 0.0).label("total_revenue"),
            func.coalesce(func.sum(Sale.total_cost), 0.0).label("total_cost"),
            func.coalesce(func.sum(Sale.total_profit), 0.0).label("total_profit"),
            func.coalesce(func.sum(Sale.quantity), 0).label("total_units"),
            func.count(Sale.id).label("total_orders"),
        )
        query = cls.apply_sales_filters(query, start_date=start_date, end_date=end_date, region=region)
        res = query.one()

        revenue = round(float(res.total_revenue), 2)
        cost = round(float(res.total_cost), 2)
        profit = round(float(res.total_profit), 2)
        units = int(res.total_units)
        orders = int(res.total_orders)

        margin = round((profit / revenue * 100), 2) if revenue > 0 else 0.0
        aov = round(revenue / orders, 2) if orders > 0 else 0.0

        return {
            "total_revenue": revenue,
            "total_cost": cost,
            "total_profit": profit,
            "gross_profit_margin_percent": margin,
            "total_units_sold": units,
            "total_orders": orders,
            "average_order_value": aov,
            "filters_applied": {
                "start_date": str(start_date) if start_date else None,
                "end_date": str(end_date) if end_date else None,
                "region": region,
            }
        }

    @classmethod
    def get_top_products(cls, limit=10, order_by="revenue", start_date=None, end_date=None, region=None, category=None) -> list:
        """
        Find top products ordered by revenue, units_sold, or profit.
        """
        query = db.session.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.category,
            func.coalesce(func.sum(Sale.total_revenue), 0.0).label("revenue"),
            func.coalesce(func.sum(Sale.total_profit), 0.0).label("profit"),
            func.coalesce(func.sum(Sale.quantity), 0).label("units_sold"),
            func.count(Sale.id).label("order_count")
        ).join(Sale, Sale.product_id == Product.id)

        query = cls.apply_sales_filters(query, start_date=start_date, end_date=end_date, region=region)

        if category:
            query = query.filter(func.lower(Product.category) == category.lower())

        query = query.group_by(Product.id, Product.sku, Product.name, Product.category)

        sort_col = {
            "revenue": desc("revenue"),
            "profit": desc("profit"),
            "units_sold": desc("units_sold"),
            "orders": desc("order_count")
        }.get(order_by, desc("revenue"))

        rows = query.order_by(sort_col).limit(limit).all()

        results = []
        for r in rows:
            rev = round(float(r.revenue), 2)
            prf = round(float(r.profit), 2)
            margin = round((prf / rev * 100), 2) if rev > 0 else 0.0
            results.append({
                "product_id": r.id,
                "sku": r.sku,
                "name": r.name,
                "category": r.category,
                "total_revenue": rev,
                "total_profit": prf,
                "units_sold": int(r.units_sold),
                "order_count": int(r.order_count),
                "profit_margin_percent": margin,
            })
        return results

    @classmethod
    def get_regional_performance(cls, start_date=None, end_date=None, region=None) -> list:
        """
        Sales and profit breakdown by geographical sales region.
        """
        query = db.session.query(
            Sale.region,
            func.coalesce(func.sum(Sale.total_revenue), 0.0).label("revenue"),
            func.coalesce(func.sum(Sale.total_profit), 0.0).label("profit"),
            func.coalesce(func.sum(Sale.quantity), 0).label("units_sold"),
            func.count(Sale.id).label("order_count"),
        )
        query = cls.apply_sales_filters(query, start_date=start_date, end_date=end_date, region=region)
        rows = query.group_by(Sale.region).order_by(desc("revenue")).all()

        total_global_rev = sum(float(r.revenue) for r in rows)

        results = []
        for r in rows:
            rev = round(float(r.revenue), 2)
            prf = round(float(r.profit), 2)
            share = round((rev / total_global_rev * 100), 2) if total_global_rev > 0 else 0.0
            margin = round((prf / rev * 100), 2) if rev > 0 else 0.0
            results.append({
                "region": r.region,
                "total_revenue": rev,
                "total_profit": prf,
                "units_sold": int(r.units_sold),
                "order_count": int(r.order_count),
                "revenue_share_percent": share,
                "profit_margin_percent": margin,
            })
        return results

    @classmethod
    def get_monthly_growth_trends(cls, start_date=None, end_date=None, region=None) -> list:
        """
        Calculates monthly sales trajectory and Month-over-Month (MoM) growth rates via Pandas.
        """
        # Group by year and month
        query = db.session.query(
            extract("year", Sale.sale_date).label("sale_year"),
            extract("month", Sale.sale_date).label("sale_month"),
            func.coalesce(func.sum(Sale.total_revenue), 0.0).label("revenue"),
            func.coalesce(func.sum(Sale.total_profit), 0.0).label("profit"),
            func.coalesce(func.sum(Sale.quantity), 0).label("units_sold"),
            func.count(Sale.id).label("order_count")
        )
        query = cls.apply_sales_filters(query, start_date=start_date, end_date=end_date, region=region)
        rows = query.group_by("sale_year", "sale_month").order_by(asc("sale_year"), asc("sale_month")).all()

        if not rows:
            return []

        data = [
            {
                "year": int(r.sale_year),
                "month": int(r.sale_month),
                "revenue": float(r.revenue),
                "profit": float(r.profit),
                "units_sold": int(r.units_sold),
                "order_count": int(r.order_count),
            }
            for r in rows
        ]

        df = pd.DataFrame(data)
        # Format year-month key
        df["period"] = df.apply(lambda row: f"{int(row['year'])}-{int(row['month']):02d}", axis=1)

        # Calculate MoM percentage changes using Pandas
        df["mom_revenue_growth_percent"] = (df["revenue"].pct_change() * 100).fillna(0.0).round(2)
        df["mom_profit_growth_percent"] = (df["profit"].pct_change() * 100).fillna(0.0).round(2)
        df["profit_margin_percent"] = np.where(df["revenue"] > 0, (df["profit"] / df["revenue"] * 100), 0.0).round(2)

        df["revenue"] = df["revenue"].round(2)
        df["profit"] = df["profit"].round(2)

        return df.to_dict(orient="records")

    @classmethod
    def get_yearly_growth_trends(cls) -> list:
        """
        Calculates annual sales trajectory and Year-over-Year (YoY) growth rates via Pandas.
        """
        query = db.session.query(
            extract("year", Sale.sale_date).label("sale_year"),
            func.coalesce(func.sum(Sale.total_revenue), 0.0).label("revenue"),
            func.coalesce(func.sum(Sale.total_profit), 0.0).label("profit"),
            func.coalesce(func.sum(Sale.quantity), 0).label("units_sold"),
            func.count(Sale.id).label("order_count")
        )
        query = cls.apply_sales_filters(query)
        rows = query.group_by("sale_year").order_by(asc("sale_year")).all()

        if not rows:
            return []

        data = [
            {
                "year": int(r.sale_year),
                "revenue": float(r.revenue),
                "profit": float(r.profit),
                "units_sold": int(r.units_sold),
                "order_count": int(r.order_count),
            }
            for r in rows
        ]

        df = pd.DataFrame(data)
        df["yoy_revenue_growth_percent"] = (df["revenue"].pct_change() * 100).fillna(0.0).round(2)
        df["yoy_profit_growth_percent"] = (df["profit"].pct_change() * 100).fillna(0.0).round(2)
        df["profit_margin_percent"] = np.where(df["revenue"] > 0, (df["profit"] / df["revenue"] * 100), 0.0).round(2)

        df["revenue"] = df["revenue"].round(2)
        df["profit"] = df["profit"].round(2)

        return df.to_dict(orient="records")

    @classmethod
    def get_top_customers(cls, limit=10, start_date=None, end_date=None, region=None) -> list:
        """
        Analyzes highest-value customer accounts and transaction frequencies.
        """
        query = db.session.query(
            Customer.id,
            Customer.customer_code,
            Customer.name,
            Customer.region,
            Customer.segment,
            func.coalesce(func.sum(Sale.total_revenue), 0.0).label("total_spend"),
            func.coalesce(func.sum(Sale.total_profit), 0.0).label("profit_generated"),
            func.coalesce(func.sum(Sale.quantity), 0).label("units_purchased"),
            func.count(Sale.id).label("order_count"),
            func.max(Sale.sale_date).label("last_purchase_date")
        ).join(Sale, Sale.customer_id == Customer.id)

        query = cls.apply_sales_filters(query, start_date=start_date, end_date=end_date, region=region)
        rows = query.group_by(
            Customer.id, Customer.customer_code, Customer.name, Customer.region, Customer.segment
        ).order_by(desc("total_spend")).limit(limit).all()

        results = []
        for r in rows:
            spend = round(float(r.total_spend), 2)
            orders = int(r.order_count)
            aov = round(spend / orders, 2) if orders > 0 else 0.0
            results.append({
                "customer_id": r.id,
                "customer_code": r.customer_code,
                "name": r.name,
                "region": r.region,
                "segment": r.segment,
                "total_spend": spend,
                "profit_generated": round(float(r.profit_generated), 2),
                "units_purchased": int(r.units_purchased),
                "order_count": orders,
                "average_order_value": aov,
                "last_purchase_date": str(r.last_purchase_date) if r.last_purchase_date else None,
            })
        return results

    @classmethod
    def get_category_performance(cls, start_date=None, end_date=None, region=None) -> list:
        """
        Analyzes sales performance aggregated by product category.
        """
        query = db.session.query(
            Product.category,
            func.coalesce(func.sum(Sale.total_revenue), 0.0).label("revenue"),
            func.coalesce(func.sum(Sale.total_profit), 0.0).label("profit"),
            func.coalesce(func.sum(Sale.quantity), 0).label("units_sold"),
            func.count(Sale.id).label("order_count")
        ).join(Sale, Sale.product_id == Product.id)

        query = cls.apply_sales_filters(query, start_date=start_date, end_date=end_date, region=region)
        rows = query.group_by(Product.category).order_by(desc("revenue")).all()

        total_rev = sum(float(r.revenue) for r in rows)

        results = []
        for r in rows:
            rev = round(float(r.revenue), 2)
            prf = round(float(r.profit), 2)
            results.append({
                "category": r.category,
                "total_revenue": rev,
                "total_profit": prf,
                "units_sold": int(r.units_sold),
                "order_count": int(r.order_count),
                "revenue_share_percent": round((rev / total_rev * 100), 2) if total_rev > 0 else 0.0,
                "profit_margin_percent": round((prf / rev * 100), 2) if rev > 0 else 0.0,
            })
        return results
