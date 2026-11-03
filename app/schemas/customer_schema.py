from marshmallow import Schema, fields, validate

VALID_REGIONS = ["North", "South", "East", "West", "Central", "International"]
VALID_SEGMENTS = ["Consumer", "SMB", "Enterprise"]

class CustomerSchema(Schema):
    id = fields.Integer(dump_only=True)
    customer_code = fields.String(required=True, validate=validate.Length(min=2, max=50))
    name = fields.String(required=True, validate=validate.Length(min=2, max=150))
    email = fields.Email(required=False, allow_none=True)
    phone = fields.String(required=False, allow_none=True, validate=validate.Length(max=50))
    region = fields.String(required=True, validate=validate.OneOf(VALID_REGIONS))
    segment = fields.String(load_default="Consumer", validate=validate.OneOf(VALID_SEGMENTS))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class CustomerUpdateSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=2, max=150))
    email = fields.Email(required=False, allow_none=True)
    phone = fields.String(required=False, allow_none=True)
    region = fields.String(required=False, validate=validate.OneOf(VALID_REGIONS))
    segment = fields.String(required=False, validate=validate.OneOf(VALID_SEGMENTS))
