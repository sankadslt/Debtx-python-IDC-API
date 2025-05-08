# custom_exceptions.py

class TaskProcessingError(Exception):
    """Base exception for task processing errors."""
    pass

class DatabaseConnectionError(TaskProcessingError):
    """Raised when there is an issue connecting to the database."""
    pass
