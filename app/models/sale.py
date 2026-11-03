from datetime import datetime, timezone, date
from app.extensions import db

class Sale(db.Model):
    """
    Sales record entity with foreign keys, computed financial metrics,
    and composite indexes for high-speed BI analytical queries.
    """
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Core Transaction Fields
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0, nullable=False)  # Decimal discount, e.g. 0.05 for 5%

    # Pre-calculated Financial Aggregates for Instant Analytical Querying
    total_revenue = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    total_profit = db.Column(db.Float, nullable=False)

    sale_date = db.Column(db.Date, nullable=False, index=True)
    region = db.Column(db.String(50), nullable=False, index=True)
    payment_method = db.Column(db.String(50), default="Credit Card", nullable=False)
    status = db.Column(db.String(50), default="Completed", nullable=False, index=True)  # Completed, Pending, Cancelled, Refunded

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Database Relationships
    customer = db.relationship("Customer", back_populates="sales")
    product = db.relationship("Product", back_populates="sales")
    user = db.relationship("User", foreign_keys=[user_id])

    # Table Indexes: Single & Composite
    __table_args__ = (
        db.Index("idx_sales_date_region", "sale_date", "region"),
        db.Index("idx_sales_customer_date", "customer_id", "sale_date"),
        db.Index("idx_sales_product_date", "product_id", "sale_date"),
    )

    def calculate_totals(self):
        """Compute financial aggregates based on quantity, price, cost, and discount."""
        gross = self.quantity * self.unit_price
        discount_amount = gross * (self.discount or 0.0)
        self.total_revenue = round(gross - discount_amount, 2)
        self.total_cost = round(self.quantity * self.unit_cost, 2)
        self.total_profit = round(self.total_revenue - self.total_cost, 2)

    def to_dict(self, include_relations=True):
        data = {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "unit_cost": self.unit_cost,
            "discount": self.discount,
            "total_revenue": self.total_revenue,
            "total_cost": self.total_cost,
            "total_profit": self.total_profit,
            "profit_margin_percent": round((self.total_profit / self.total_revenue * 100), 2) if self.total_revenue > 0 else 0.0,
            "sale_date": self.sale_date.isoformat() if isinstance(self.sale_date, (date, datetime)) else str(self.sale_date),
            "region": self.region,
            "payment_method": self.payment_method,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_relations:
            if self.customer:
                data["customer"] = {
                    "customer_code": self.customer.customer_code,
                    "name": self.customer.name,
                    "region": self.customer.region,
                    "segment": self.customer.segment,
                }
            if self.product:
                data["product"] = {
                    "sku": self.product.sku,
                    "name": self.product.name,
                    "category": self.product.category,
                }
        return data

    def __repr__(self):
        return f"<Sale {self.transaction_id} - Rev: ${self.total_revenue}>"
