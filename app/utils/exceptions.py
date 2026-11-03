"""
Custom API Exceptions for centralized error management.
"""

class APIException(Exception):
    """Base class for domain and API errors."""
    status_code = 500
    error_code = "INTERNAL_SERVER_ERROR"

    def __init__(self, message=None, details=None, status_code=None, error_code=None):
        super().__init__()
        if message:
            self.message = message
        else:
            self.message = "An unexpected error occurred."
            
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.details = details

    def to_dict(self):
        rv = {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            }
        }
        return rv


class ValidationError(APIException):
    status_code = 400
    error_code = "VALIDATION_ERROR"

    def __init__(self, message="Invalid request payload", details=None):
        super().__init__(message=message, details=details, status_code=400, error_code="VALIDATION_ERROR")


class ResourceNotFoundError(APIException):
    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"

    def __init__(self, resource="Resource", identifier=None):
        if identifier:
            message = f"{resource} with identifier '{identifier}' was not found."
        else:
            message = f"{resource} was not found."
        super().__init__(message=message, status_code=404, error_code="RESOURCE_NOT_FOUND")


class ConflictError(APIException):
    status_code = 409
    error_code = "CONFLICT_ERROR"

    def __init__(self, message="Resource conflict encountered", details=None):
        super().__init__(message=message, details=details, status_code=409, error_code="CONFLICT_ERROR")


class UnauthorizedError(APIException):
    status_code = 401
    error_code = "UNAUTHORIZED"

    def __init__(self, message="Authentication required"):
        super().__init__(message=message, status_code=401, error_code="UNAUTHORIZED")


class ForbiddenError(APIException):
    status_code = 403
    error_code = "FORBIDDEN"

    def __init__(self, message="You do not have permission to perform this action"):
        super().__init__(message=message, status_code=403, error_code="FORBIDDEN")


class FileProcessingError(APIException):
    status_code = 422
    error_code = "FILE_PROCESSING_ERROR"

    def __init__(self, message="Failed to parse or process uploaded dataset", details=None):
        super().__init__(message=message, details=details, status_code=422, error_code="FILE_PROCESSING_ERROR")
