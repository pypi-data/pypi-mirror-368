import json
import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

def safe_clean_json_text(text: str, fallback: Any = {}) -> dict | Any:
    try:
        # First, clean up JavaScript date constructors
        cleaned_text = clean_js_dates_in_json(text)
        return json.loads(cleaned_text)
    except Exception as e:
        logger.info(f"Error cleaning JSON string: {e}")
        return fallback


def clean_js_dates_in_json(text: str) -> str:
    """
    Convert JavaScript Date constructors to ISO date strings in JSON text.
    
    Handles patterns like:
    - new Date(1753942920901)
    - new Date("2023-12-01")
    """
    # Pattern to match new Date(timestamp) or new Date("date-string")
    date_pattern = r'new Date\(([^)]+)\)'
    
    def replace_date(match):
        date_arg = match.group(1).strip()
        
        try:
            # If it's a numeric timestamp
            if date_arg.isdigit():
                timestamp = int(date_arg)
                # Convert milliseconds to seconds for Python datetime
                dt = datetime.fromtimestamp(timestamp / 1000)
                return f'"{dt.isoformat()}"'
            
            # If it's already a quoted string, just return it as is
            elif date_arg.startswith('"') and date_arg.endswith('"'):
                return date_arg
            
            # If it's an unquoted string, quote it
            else:
                return f'"{date_arg}"'
                
        except (ValueError, OverflowError) as e:
            # If we can't parse the date, return null
            logger.info(f"Error parsing date: {e}")
            return 'null'
    
    # Replace all JavaScript date constructors
    cleaned = re.sub(date_pattern, replace_date, text)
    return cleaned

def try_get_pretty_json(text: str) -> str:
    try:
        return json.dumps(json.loads(text), sort_keys=True, indent=4)
    except Exception as e:
        logger.info(f"Error getting pretty JSON: {e}")
        return text
