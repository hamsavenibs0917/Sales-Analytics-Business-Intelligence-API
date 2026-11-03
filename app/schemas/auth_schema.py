from marshmallow import Schema, fields, validate, validates, ValidationError

class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.String(required=True, validate=validate.Length(min=6, max=100))
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    role = fields.String(
        load_default="user",
        validate=validate.OneOf(["admin", "analyst", "user"], error="Role must be admin, analyst, or user.")
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class RefreshTokenSchema(Schema):
    refresh_token = fields.String(required=False)
