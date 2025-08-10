# versao final
# src/totaltimeformatter/formatter.py

import math
from datetime import datetime, timedelta

# Define constants for precision modes
TRUNCATE = 0
ROUND_UP = 1
KEEP_PRECISION = 2

def format_total_hours(
    time_input: object,
    precision_mode: int = TRUNCATE
) -> str:
    """
    Converts a time input (string or timedelta) into a total duration format (HH:MM:SS).
    """
    duration = timedelta()
    
    # --- Input Processing (same as before) ---
    if isinstance(time_input, timedelta):
        duration = time_input
    elif isinstance(time_input, str):
        time_str = time_input.strip()
        try:
            if "-" in time_str and " " in time_str:
                format_code = "%Y-%m-%d %H:%M:%S"
                if "." in time_str:
                    format_code += ".%f"
                target_date = datetime.strptime(time_str, format_code)
                reference_date = datetime(1899, 12, 31)
                duration = target_date - reference_date
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
    else:
        return "Error: Input must be a string or a timedelta object."

    # --- Final Formatting Logic ---
    if precision_mode == KEEP_PRECISION:
        # --- PRECISE LOGIC ---
        # 1. Calculate total integer seconds from the precise components
        total_seconds_int = duration.days * 86400 + duration.seconds
        
        # 2. Get hours, minutes, and integer seconds
        total_minutes, seconds = divmod(total_seconds_int, 60)
        hours, minutes = divmod(total_minutes, 60)
        
        # 3. Get the fractional part as a precise integer (0-999999)
        microseconds = duration.microseconds
        
        if microseconds > 0:
            # Convert to string, pad with leading zeros, then strip trailing zeros
            fractional_str = f"{microseconds:06d}".rstrip('0')
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{fractional_str}"
        else:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Logic for TRUNCATE and ROUND_UP (unchanged)
    total_seconds = 0
    if precision_mode == ROUND_UP:
        total_seconds = math.ceil(duration.total_seconds())
    else: # TRUNCATE
        total_seconds = int(duration.total_seconds())

    total_minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(total_minutes, 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"