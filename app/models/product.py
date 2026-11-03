from datetime import datetime, timezone
from app.extensions import db

class Product(db.Model):
    """Product catalog entity with category, manufacturing cost, and retail pricing."""
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    unit_cost = db.Column(db.Float, nullable=False, default=0.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    sales = db.relationship("Sale", back_populates="product", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def gross_margin_percent(self) -> float:
        """Calculates expected margin percentage for the catalog product."""
        if self.unit_price > 0:
            return round(((self.unit_price - self.unit_cost) / self.unit_price) * 100, 2)
        return 0.0

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "unit_cost": self.unit_cost,
            "unit_price": self.unit_price,
            "gross_margin_percent": self.gross_margin_percent,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Product {self.sku} - {self.name}>"
