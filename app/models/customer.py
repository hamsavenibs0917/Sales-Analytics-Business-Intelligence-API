from datetime import datetime, timezone
from app.extensions import db

class Customer(db.Model):
    """Customer entity with regional and market segment data."""
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    region = db.Column(db.String(50), nullable=False, index=True)  # North, South, East, West, Central, International
    segment = db.Column(db.String(50), default="Consumer", nullable=False)  # Enterprise, SMB, Consumer
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    sales = db.relationship("Sale", back_populates="customer", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_code": self.customer_code,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "region": self.region,
            "segment": self.segment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Customer {self.customer_code} - {self.name}>"
