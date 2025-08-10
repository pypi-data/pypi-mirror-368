# src/totaltimeformatter/__init__.py

# Import the main function from the formatter module
from .formatter import format_total_hours

# Import and export the mode constants so they are accessible to users
from .formatter import TRUNCATE, ROUND_UP, KEEP_PRECISION

# Define what gets imported when a user does 'from totaltimeformatter import *'
__all__ = [
    'format_total_hours',
    'TRUNCATE',
    'ROUND_UP',
    'KEEP_PRECISION'
]