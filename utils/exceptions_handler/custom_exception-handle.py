"""
    Purpose: This template is used for the DRC Routes.
    Created Date: 2025-01-16
    Created By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
    Last Modified Date: 2024-01-26
    Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)       
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: product_manager.py, product_manager_class.py, dateTimeValidator.py
    Notes:
"""

# utils/exception/custom_exception.py

class CustomException(Exception):
    """Base class for all custom exceptions"""
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class DatabaseError(CustomException):
    """Exception raised for database-related errors."""
    def __init__(self, message: str = "A database error occurred"):
        super().__init__(message, 500)  # HTTP Status 500 for Internal Server Error

class ValidationError(CustomException):
    """Exception raised for validation errors."""
    def __init__(self, message: str = "Invalid data provided"):
        super().__init__(message, 400)  # HTTP Status 400 for Bad Request

class NotFoundError(CustomException):
    """Exception raised when a resource is not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)  # HTTP Status 404 for Not Found

class UnauthorizedError(CustomException):
    """Exception raised for unauthorized access errors."""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, 401)  # HTTP Status 401 for Unauthorized

class BadRequestError(CustomException):
    """Exception raised for bad requests."""
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, 400)  # HTTP Status 400 for Bad Request
