"""
Utility functions for the AgriDefender application.
"""
import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

def generate_id() -> str:
    """Generate a unique ID for database records."""
    return str(uuid.uuid4())

def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format a datetime object as ISO 8601 string."""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {}
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        return {}

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to a JSON file."""
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {str(e)}")
        return False

def validate_coordinates(lon: float, lat: float) -> bool:
    """Validate geographic coordinates."""
    return -180 <= lon <= 180 and -90 <= lat <= 90

def calculate_distance(point1: List[float], point2: List[float]) -> float:
    """
    Calculate the Euclidean distance between two points.
    For geographic coordinates, this is an approximation.
    """
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def get_env_variable(name: str, default: Any = None) -> Any:
    """Get an environment variable with a default value."""
    return os.environ.get(name, default)

def parse_boolean(value: Union[str, bool]) -> bool:
    """Parse a string as a boolean value."""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('yes', 'true', 't', '1', 'y')
    
    return bool(value)

def format_error_response(error_message: str, error_code: int = 500, details: Any = None) -> Dict[str, Any]:
    """Format a standardized error response."""
    return {
        "error": error_message,
        "code": error_code,
        "details": details
    }
