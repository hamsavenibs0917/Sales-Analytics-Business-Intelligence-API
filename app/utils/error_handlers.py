from flask import jsonify, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from werkzeug.exceptions import HTTPException
from app.utils.exceptions import APIException
from app.extensions import jwt

def register_error_handlers(app):
    """Register centralized error handlers for consistent JSON API responses."""

    @app.errorhandler(APIException)
    def handle_api_exception(err):
        response = jsonify(err.to_dict())
        response.status_code = err.status_code
        return response

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_error(err):
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": err.messages
            }
        }), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return jsonify({
            "success": False,
            "error": {
                "code": err.name.upper().replace(" ", "_"),
                "message": err.description,
                "details": None
            }
        }), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(err):
        current_app.logger.exception(f"Unhandled exception occurred: {err}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "details": str(err) if current_app.debug else None
            }
        }), 500

    # Configure JWT callback responses
    @jwt.unauthorized_loader
    def custom_unauthorized_response(callback):
        return jsonify({
            "success": False,
            "error": {
                "code": "AUTHORIZATION_HEADER_MISSING",
                "message": "Missing Authorization Header. Include 'Authorization: Bearer <token>'",
                "details": callback
            }
        }), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(callback):
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_TOKEN",
                "message": "The provided authentication token is invalid or malformed",
                "details": callback
            }
        }), 401

    @jwt.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "error": {
                "code": "TOKEN_EXPIRED",
                "message": "The authentication token has expired. Please refresh your token.",
                "details": None
            }
        }), 401

    @jwt.revoked_token_loader
    def custom_revoked_token_response(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "error": {
                "code": "TOKEN_REVOKED",
                "message": "The token has been revoked",
                "details": None
            }
        }), 401
