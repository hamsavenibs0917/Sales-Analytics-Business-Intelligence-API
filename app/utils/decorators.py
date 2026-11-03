from functools import wraps
from flask import request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from app.utils.exceptions import ForbiddenError, UnauthorizedError, ValidationError
from app.models.user import User

def role_required(allowed_roles):
    """
    Decorator to enforce Role-Based Access Control (RBAC).
    Usage:
        @role_required(["admin"])
        @role_required(["admin", "analyst"])
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")

            # Fallback check against DB if role is not present in claims
            if not user_role:
                user_id = get_jwt_identity()
                user = db.session.get(User, int(user_id)) if user_id and str(user_id).isdigit() else None
                if not user or not user.is_active:
                    raise UnauthorizedError("User account is inactive or not found.")
                user_role = user.role

            if user_role not in allowed_roles:
                raise ForbiddenError(f"Access forbidden: requires one of {allowed_roles} roles. Your role is '{user_role}'.")
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def validate_payload(schema_cls):
    """
    Decorator to validate request JSON body using a Marshmallow schema.
    Injects validated data into g.validated_data.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Request body must be valid JSON.")
            payload = request.get_json() or {}
            schema = schema_cls() if isinstance(schema_cls, type) else schema_cls
            errors = schema.validate(payload)
            if errors:
                raise ValidationError("Payload validation failed.", details=errors)
            g.validated_data = schema.load(payload)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
