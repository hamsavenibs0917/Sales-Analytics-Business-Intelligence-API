from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.extensions import db
from app.models.user import User
from app.schemas.auth_schema import RegisterSchema, LoginSchema
from app.utils.decorators import validate_payload
from app.utils.exceptions import ConflictError, UnauthorizedError, ResourceNotFoundError

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@validate_payload(RegisterSchema)
def register():
    """Register a new user account."""
    data = g.validated_data
    if User.query.filter_by(email=data["email"].lower()).first():
        raise ConflictError(f"User with email '{data['email']}' already exists.")

    user = User(
        email=data["email"].lower(),
        full_name=data["full_name"],
        role=data.get("role", "user"),
        is_active=True
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "User registered successfully.",
        "user": user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
@validate_payload(LoginSchema)
def login():
    """Authenticate user and return JWT access and refresh tokens."""
    data = g.validated_data
    user = User.query.filter_by(email=data["email"].lower()).first()

    if not user or not user.check_password(data["password"]):
        raise UnauthorizedError("Invalid email or password.")

    if not user.is_active:
        raise UnauthorizedError("User account has been disabled.")

    # Attach claims to the access token for instant RBAC verification
    additional_claims = {
        "role": user.role,
        "email": user.email,
        "full_name": user.full_name
    }
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "success": True,
        "message": "Authentication successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "user": user.to_dict()
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    """Generate a new access token using a valid refresh token."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or account inactive.")

    additional_claims = {
        "role": user.role,
        "email": user.email,
        "full_name": user.full_name
    }
    new_access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    return jsonify({
        "success": True,
        "access_token": new_access_token,
        "token_type": "Bearer"
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Retrieve profile of currently authenticated user."""
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        raise ResourceNotFoundError("User", user_id)

    return jsonify({
        "success": True,
        "user": user.to_dict()
    }), 200
