from marshmallow import Schema, fields, validate

class ProductSchema(Schema):
    id = fields.Integer(dump_only=True)
    sku = fields.String(required=True, validate=validate.Length(min=2, max=50))
    name = fields.String(required=True, validate=validate.Length(min=2, max=150))
    category = fields.String(required=True, validate=validate.Length(min=2, max=100))
    unit_cost = fields.Float(required=True, validate=validate.Range(min=0.0))
    unit_price = fields.Float(required=True, validate=validate.Range(min=0.0))
    is_active = fields.Boolean(load_default=True)
    gross_margin_percent = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProductUpdateSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=2, max=150))
    category = fields.String(required=False, validate=validate.Length(min=2, max=100))
    unit_cost = fields.Float(required=False, validate=validate.Range(min=0.0))
    unit_price = fields.Float(required=False, validate=validate.Range(min=0.0))
    is_active = fields.Boolean(required=False)
