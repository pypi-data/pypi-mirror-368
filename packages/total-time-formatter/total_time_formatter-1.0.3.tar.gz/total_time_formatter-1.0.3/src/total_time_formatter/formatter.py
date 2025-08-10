import math
import pandas as pd
from datetime import datetime, timedelta, time

# Define constants for precision modes
TRUNCATE = 0
ROUND_UP = 1
KEEP_PRECISION = 2

def format_total_hours(
    time_input: object,
    precision_mode: int = TRUNCATE,
    reference_date: str = '1899-12-31 00:00:00'
) -> str:
    duration = timedelta()
    
    if isinstance(time_input, timedelta):
        duration = time_input
        
    elif isinstance(time_input, (datetime, pd.Timestamp)):
        try:
            reference_date_obj = datetime.strptime(reference_date, "%Y-%m-%d %H:%M:%S")
            duration = time_input - reference_date_obj
        except (ValueError, TypeError):
             return "Error: Invalid reference_date format or type mismatch."

    elif isinstance(time_input, time):
        # Treat a time object as a duration from midnight
        duration = timedelta(
            hours=time_input.hour,
            minutes=time_input.minute,
            seconds=time_input.second,
            microseconds=time_input.microsecond
        )

    elif isinstance(time_input, str):
        time_str = time_input.strip()
        try:
            # Full datetime string: "YYYY-MM-DD HH:MM:SS"
            if "-" in time_str and " " in time_str:
                format_code = "%Y-%m-%d %H:%M:%S"
                if "." in time_str:
                    format_code += ".%f"
                target_date = datetime.strptime(time_str, format_code)
                
                try:
                    reference_date_obj = datetime.strptime(reference_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return f"Error: Invalid reference_date format. Use 'YYYY-MM-DD HH:MM:SS'."
                duration = target_date - reference_date_obj
            
            # Time-only string: "HH:MM:SS"
            elif ":" in time_str:
                parts = time_str.split(':')
                h = int(parts[0])
                m = int(parts[1])
                s_float = float(parts[2]) if len(parts) > 2 else 0.0
                duration = timedelta(hours=h, minutes=m, seconds=s_float)
            else:
                raise ValueError("Unrecognized string format.")
        except (ValueError, IndexError) as e:
            return f"Error processing string '{time_input}': {e}"
    
    # Handle unexpected types
    else:
        # Check for null values from pandas (NaT, None, nan)
        if pd.isna(time_input):
            return None # Or return '00:00:00' or an empty string if you prefer
        return f"Error: Input type '{type(time_input).__name__}' is not supported."

    if precision_mode == KEEP_PRECISION:
        total_seconds_int = duration.days * 86400 + duration.seconds
        total_minutes, seconds = divmod(total_seconds_int, 60)
        hours, minutes = divmod(total_minutes, 60)
        microseconds = duration.microseconds
        if microseconds > 0:
            fractional_str = f"{microseconds:06d}".rstrip('0')
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{fractional_str}"
        else:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Logic for TRUNCATE and ROUND_UP
    total_seconds = 0
    if precision_mode == ROUND_UP:
        total_seconds = math.ceil(duration.total_seconds())
    else: # TRUNCATE
        total_seconds = int(duration.total_seconds())

    total_minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(total_minutes, 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"