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

from datetime import datetime

def human_readable_dateTime_to_datetime(value):
    """
    Custom validator to parse human-readable datetime to a datetime object.
    """
    if isinstance(value, datetime):
        return value  # if already a datetime object
    if value is None:
        return None
    try:
        # Parse the human-readable datetime string
        return datetime.strptime(value, "%m/%d/%Y %H:%M:%S")
    except ValueError as e:
        raise ValueError(
            f"Invalid datetime format: {value}. "
            f"Expected format: 'mm/dd/yyyy 24HH:MM:SS'. Example: '01/26/2025 20:14:19'"
        ) from e