from utils.logger.loggers import SingletonLogger
from fastapi import HTTPException 
import json

SingletonLogger.configure()

logger = SingletonLogger.get_logger('appLogger')

class BaseCustomException(Exception):
    """
    Base class for all custom exceptions.
    """
    status_code = 400  # Default HTTP status code

    def __init__(self, message="An error occurred"):
        self.message = message
        logger.error(f"{self.__class__.__name__}: {message}")  # Log error during initialization
        super().__init__(message)

    def to_http_exception(self):
        """
        Convert the custom exception into an HTTPException.
        """
        return HTTPException(
            status_code=self.status_code,
            detail={"status_code":self.status_code ,"status": "failed", "Message":self.message}
        )


class DatabaseConnectionError(BaseCustomException):
    """Raised when the connection to the database fails."""
    
    status_code =500
    
    def __init__(self, message="Database connection failed"):
        super().__init__(message)
        
class ValidationError(BaseCustomException):
    """Raised when validation of input or response data fails."""

    status_code = 422  # Unprocessable Entity

    def __init__(self, message="Validation failed"):
        super().__init__(message)
        
class InvalidIncidentIDError(BaseCustomException):
    """Raised when the Incident_ID is not permitted by configuration."""
    
    status_code = 400
    
    def __init__(self, message="Incident_ID is not found"):
        super().__init__(message)


class DocumentNotFoundError(BaseCustomException):
    """Raised when the requested document is not found."""
    
    status_code = 404
    
    def __init__(self, message="Document not found"):
        super().__init__(message)


class DataFetchError(BaseCustomException):
    """Raised when an error occurs while fetching data."""
    
    status_code = 500
    
    def __init__(self, message="An error occurred while fetching the data"):
        super().__init__(message)


class DataInsertError(BaseCustomException):
    """Raised when an error occurs while inserting data."""
    
    status_code = 500
    
    def __init__(self, message="An error occurred while inserting data"):
        super().__init__(message)


class NoValidDataError(BaseCustomException):
    """Raised when no valid data is available for insertion."""
    
    status_code = 400
    
    def __init__(self, message="No valid data to insert"):
        super().__init__(message)


class ProcessingError(BaseCustomException):
    """Raised when an error occurs while processing an individual task."""
    
    status_code = 500
    
    def __init__(self, message="Error processing task"):
        super().__init__(message)


class TaskIdNotFoundError(BaseCustomException):
    """Raised when the task ID is not found."""
    def __init__(self, message="Task ID not found"):
        super().__init__(message)


class CaseIdNotFoundError(BaseCustomException):
    """Raised when the case ID is not found."""
    
    status_code = 404
    
    def __init__(self, message="Case ID not found"):
        super().__init__(message)


class FileMissingError(BaseCustomException):
    """Raised when a required file is missing."""
    
    status_code = 404
    
    def __init__(self, message="File not found"):
        super().__init__(message)


class DocumentUpdateError(BaseCustomException):
    """Raised when a document update fails."""
    
    status_code = 500
    
    def __init__(self, message="Document update failed"):
        super().__init__(message)


class NotModifiedResponse(BaseCustomException):
    """Raised when the response is not modified."""
    
    status_code = 304
    
    def __init__(self, message="Not Modified Response"):
        super().__init__(message)

class InvalidDataError(BaseCustomException):
    """Raised when invalid or missing data is encountered."""

    status_code = 400

    def __init__(self, message="Invalid or missing data encountered"):
        super().__init__(message)
