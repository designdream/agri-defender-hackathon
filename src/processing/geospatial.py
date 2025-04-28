import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
import json
import uuid
import pyproj
from shapely.geometry import Point, Polygon, mapping, shape
from shapely.ops import transform
import geopandas as gpd
from functools import partial

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Constants for different threat spread patterns
SPREAD_RATES = {
    'FUNGAL': {
        'LOW': 2.0,       # meters per day
        'MEDIUM': 5.0,
        'HIGH': 10.0,
        'CRITICAL': 25.0
    },
    'BACTERIAL': {
        'LOW': 3.0,
        'MEDIUM': 7.0,
        'HIGH': 15.0,
        'CRITICAL': 30.0
    },
    'VIRAL': {
        'LOW': 5.0,
        'MEDIUM': 10.0,
        'HIGH': 25.0,
        'CRITICAL': 50.0
    },
    'PEST': {
        'LOW': 8.0,
        'MEDIUM': 15.0,
        'HIGH': 30.0,
        'CRITICAL': 60.0
    },
    'UNKNOWN': {
        'LOW': 2.0,
        'MEDIUM': 5.0,
        'HIGH': 10.0,
        'CRITICAL': 20.0
    },
    'BIOWEAPON': {
        'LOW': 10.0,
        'MEDIUM': 25.0,
        'HIGH': 50.0,
        'CRITICAL': 100.0
    }
}

# Wind influence factors for different threat types
WIND_INFLUENCE = {
    'FUNGAL': 0.7,      # Fungal spores are heavily influenced by wind
    'BACTERIAL': 0.5,   # Bacterial spread somewhat influenced by wind
    'VIRAL': 0.8,       # Viral spread heavily influenced by wind (insect vectors)
    'PEST': 0.6,        # Pests can travel with wind
    'UNKNOWN': 0.5,
    'BIOWEAPON': 0.9    # Assumed to be designed for efficient spread
}

# Dominant spread pattern shapes for different threat types
SPREAD_PATTERNS = {
    'FUNGAL': 'circle',       # Tends to spread in all directions
    'BACTERIAL': 'circle',    # Similar to fungal
    'VIRAL': 'ellipse',       # Often directional with wind/vectors
    'PEST': 'ellipse',        # Often follows wind or crop rows
    'UNKNOWN': 'circle',
    'BIOWEAPON': 'custom'     # Could be engineered for specific patterns
}


def map_threat_area(
    location: Dict[str, Any], 
    threat_type: str, 
    sensor_id: str, 
    radius_meters: float = 100.0
) -> Dict[str, Any]:
    """
    Map the potentially affected area around a detected threat.
    
    Args:
        location: GeoJSON Point representing the threat location
        threat_type: Type of biological threat
        sensor_id: ID of the sensor that detected the threat
        radius_meters: Initial radius of affected area in meters
        
    Returns:
        GeoJSON Polygon representing the potentially affected area
    """
    try:
        logger.info(f"Mapping threat area for {threat_type} at {location}")
        
        # Extract coordinates from the GeoJSON Point
        if location.get('type') != 'Point':
            logger.warning(f"Invalid location format: {location}")
            return None
        
        # Get coordinates (longitude, latitude)
        coords = location.get('coordinates', [0, 0])
        lon, lat = coords
        
        # Create a point from the coordinates
        point = Point(lon, lat)
        
        # Create a circular buffer around the point
        # We need to convert to a projected CRS to make the buffer in meters
        
        # Define the source CRS (WGS84) and target projected CRS (UTM zone for this location)
        src_crs = pyproj.CRS('EPSG:4326')  # WGS84
        
        # Calculate UTM zone from longitude
        utm_zone = int(math.floor((lon + 180) / 6) + 1)
        target_crs = pyproj.CRS(f'EPSG:326{utm_zone:02d}' if lat >= 0 else f'EPSG:327{utm_zone:02d}')
        
        # Create the transformer
        project = pyproj.Transformer.from_crs(src_crs, target_crs, always_xy=True).transform
        project_back = pyproj.Transformer.from_crs(target_crs, src_crs, always_xy=True).transform
        
        # Transform the point, create buffer, and transform back
        point_utm = transform(project, point)
        buffer_utm = point_utm.buffer(radius_meters)
        buffer_wgs84 = transform(project_back, buffer_utm)
        
        # Convert to GeoJSON
        affected_area = mapping(buffer_wgs84)
        
        logger.info(f"Created affected area with radius {radius_meters}m for {threat_type}")
        return affected_area
        
    except Exception as e:
        logger.error(f"Error mapping threat area: {str(e)}")
        return None


def predict_spread(
    threat_id: str, 
    threat_type: str, 
    location: Dict[str, Any], 
    detection_time: str, 
    current_weather: Dict[str, Any] = None,
    days_to_predict: int = 7
) -> List[Dict[str, Any]]:
    """
    Predict how a biological threat will spread over time.
    
    Args:
        threat_id: Unique identifier for the threat
        threat_type: Type of biological threat
        location: GeoJSON Point representing the initial threat location
        detection_time: ISO-format timestamp of when the threat was detected
        current_weather: Dictionary with current weather data
        days_to_predict: Number of days ahead to predict
        
    Returns:
        List of prediction objects for different time points
    """
    try:
        logger.info(f"Generating spread predictions for {threat_type} threat {threat_id}")
        
        # Parse detection time
        detection_dt = datetime.fromisoformat(detection_time.replace("Z", "+00:00"))
        
        # Default weather if none provided
        if not current_weather:
            current_weather = {
                'temperature': 25.0,
                'humidity': 60.0,
                'wind_speed': 5.0,
                'wind_direction': 180.0,
                'precipitation': 0.0
            }
        
        # Extract location coordinates
        if location.get('type') != 'Point':
            logger.warning(f"Invalid location format: {location}")
            return []
        
        coords = location.get('coordinates', [0, 0])
        lon, lat = coords
        
        # Define base spread rate based on threat type
        # Default to MEDIUM severity if not specified
        base_spread_rate = SPREAD_RATES.get(threat_type, SPREAD_RATES['UNKNOWN'])['MEDIUM']
        
        # Adjust spread rate based on environmental factors
        adjusted_rate = adjust_spread_rate(base_spread_rate, threat_type, current_weather)
        
        # Get wind influence factor for this threat type
        wind_factor = WIND_INFLUENCE.get(threat_type, 0.5)
        
        # Get preferred spread pattern for this threat type
        pattern = SPREAD_PATTERNS.get(threat_type, 'circle')
        
        # Generate predictions for each day
        predictions = []
        
        for day in range(1, days_to_predict + 1):
            # Calculate prediction time
            prediction_time = detection_dt + timedelta(days=day)
            
            # Calculate cumulative spread distance
            spread_distance = adjusted_rate * day
            
            # Determine threat level for this day's prediction
            # Threat level typically increases over time if unchecked
            if day <= 2:
                severity = "LOW" if day == 1 else "MEDIUM"
            elif day <= 5:
                severity = "MEDIUM" if day <= 3 else "HIGH"
            else:
                severity = "HIGH" if day <= 6 else "CRITICAL"
                
            # Calculate confidence (decreases over time due to increasing uncertainty)
            confidence = max(0.4, 0.9 - (day * 0.05))
            
            # Calculate probability (also decreases over time)
            probability = max(0.3, 0.9 - (day * 0.07))
            
            # Generate the spread area based on the pattern
            affected_area = generate_spread_area(
                lon, lat, 
                spread_distance, 
                pattern, 
                current_weather.get('wind_direction', 0), 
                current_weather.get('wind_speed', 0),
                wind_factor
            )
            
            # Calculate the new center point for the threat (it may move)
            # For directional threats, the center will shift in the wind direction
            new_center = calculate_new_center(
                lon, lat,
                day * adjusted_rate * wind_factor * 0.3,  # Center shifts somewhat in wind direction
                current_weather.get('wind_direction', 0)
            )
            
            # Create prediction object
            prediction = {
                'threat_id': threat_id,
                'prediction_time': prediction_time.isoformat(),
                'threat_level': severity,
                'confidence': confidence,
                'probability': probability,
                'location': {
                    'type': 'Point',
                    'coordinates': new_center
                },
                'affected_area': affected_area,
                'spread_velocity': adjusted_rate,
                'day': day
            }
            
            predictions.append(prediction)
        
        logger.info(f"Generated {len(predictions)} spread predictions for threat {threat_id}")
        return predictions
        
    except Exception as e:
        logger.error(f"Error predicting threat spread: {str(e)}")
        return []


def adjust_spread_rate(
    base_rate: float, 
    threat_type: str, 
    weather: Dict[str, Any]
) -> float:
    """
    Adjust the base spread rate based on environmental factors.
    
    Args:
        base_rate: Base spread rate in meters per day
        threat_type: Type of biological threat
        weather: Dictionary with current weather data
        
    Returns:
        Adjusted spread rate
    """
    adjusted_rate = base_rate
    
    # Adjust based on temperature
    temp = weather.get('temperature', 25.0)
    if threat_type in ['FUNGAL', 'BACTERIAL']:
        # These thrive in warm but not extremely hot conditions
        if temp < 10:
            adjusted_rate *= 0.5  # Cold slows growth
        elif 20 <= temp <= 30:
            adjusted_rate *= 1.5  # Optimal temperature
        elif temp > 35:
            adjusted_rate *= 0.7  # Too hot
    elif threat_type == 'VIRAL':
        # Some viruses spread better in cooler weather
        if 10 <= temp <= 20:
            adjusted_rate *= 1.3
    elif threat_type == 'PEST':
        # Insects typically more active in warm weather
        if temp > 25:
            adjusted_rate *= 1.4
    
    # Adjust based on humidity
    humidity = weather.get('humidity', 60.0)
    if threat_type == 'FUNGAL':
        # Fungi thrive in humid conditions
        if humidity > 70:
            adjusted_rate *= 1.6
        elif humidity < 40:
            adjusted_rate *= 0.6
    elif threat_type == 'BACTERIAL':
        # Bacteria also prefer humidity
        if humidity > 60:
            adjusted_rate *= 1.4
        
    # Adjust based on precipitation
    precip = weather.get('precipitation', 0.0)
    if precip > 0:
        if threat_type in ['FUNGAL', 'BACTERIAL']:
            adjusted_rate *= 1.0 + min(1.0, precip / 10.0)  # Increase with rain
        elif threat_type == 'PEST':
            adjusted_rate *= max(0.5, 1.0 - (precip / 20.0))  # Decrease with heavy rain
    
    # Adjust based on wind speed
    wind_speed = weather.get('wind_speed', 5.0)
    if wind_speed > 10:
        # Strong winds help spread airborne threats
        if threat_type in ['FUNGAL', 'VIRAL']:
            adjusted_rate *= 1.0 + min(1.0, (wind_speed - 10) / 20.0)
    
    return adjusted_rate


def generate_spread_area(
    lon: float, 
    lat: float, 
    distance: float, 
    pattern: str, 
    wind_direction: float, 
    wind_speed: float,
    wind_factor: float
) -> Dict[str, Any]:
    """
    Generate a GeoJSON polygon representing the spread area.
    
    Args:
        lon: Longitude of the center point
        lat: Latitude of the center point
        distance: Distance of spread in meters
        pattern: Type of spread pattern ('circle', 'ellipse', 'custom')
        wind_direction: Wind direction in degrees
        wind_speed: Wind speed in m/s
        wind_factor: How much wind influences the spread (0-1)
        
    Returns:
        GeoJSON Polygon representing the spread area
    """
    try:
        # Define the source CRS (WGS84) and target projected CRS (UTM zone for this location)
        src_crs = pyproj.CRS('EPSG:4326')  # WGS84
        
        # Calculate UTM zone from longitude
        utm_zone = int(math.floor((lon + 180) / 6) + 1)
        target_crs = pyproj.CRS(f'EPSG:326{utm_zone:02d}' if lat >= 0 else f'EPSG:327{utm_zone:02d}')
        
        # Create transformers
        project = pyproj.Transformer.from_crs(src_crs, target_crs, always_xy=True).transform
        project_back = pyproj.Transformer.from_crs(target_crs, src_crs, always_xy=True).transform
        
        # Create center point
        center = Point(lon, lat)
        center_utm = transform(project, center)
        
        if pattern == 'circle':
            # Create a circular buffer
            spread_area_utm = center_utm.buffer(distance)
        
        

