from marshmallow import Schema, fields, validate

VALID_STATUSES = ["Completed", "Pending", "Cancelled", "Refunded"]
VALID_PAYMENT_METHODS = ["Credit Card", "Bank Transfer", "PayPal", "Invoice", "Cash"]

class SaleCreateSchema(Schema):
    transaction_id = fields.String(required=True, validate=validate.Length(min=3, max=100))
    customer_id = fields.Integer(required=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    unit_price = fields.Float(required=True, validate=validate.Range(min=0.01))
    unit_cost = fields.Float(required=False, validate=validate.Range(min=0.0))  # Optional: defaults to product.unit_cost
    discount = fields.Float(load_default=0.0, validate=validate.Range(min=0.0, max=1.0))
    sale_date = fields.Date(required=True)
    region = fields.String(required=True, validate=validate.Length(min=2, max=50))
    payment_method = fields.String(load_default="Credit Card", validate=validate.OneOf(VALID_PAYMENT_METHODS))
    status = fields.String(load_default="Completed", validate=validate.OneOf(VALID_STATUSES))


class SaleUpdateSchema(Schema):
    quantity = fields.Integer(required=False, validate=validate.Range(min=1))
    unit_price = fields.Float(required=False, validate=validate.Range(min=0.01))
    unit_cost = fields.Float(required=False, validate=validate.Range(min=0.0))
    discount = fields.Float(required=False, validate=validate.Range(min=0.0, max=1.0))
    sale_date = fields.Date(required=False)
    region = fields.String(required=False, validate=validate.Length(min=2, max=50))
    payment_method = fields.String(required=False, validate=validate.OneOf(VALID_PAYMENT_METHODS))
    status = fields.String(required=False, validate=validate.OneOf(VALID_STATUSES))
