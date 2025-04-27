from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union, Any
from enum import Enum
from datetime import datetime
import uuid
from geojson_pydantic import Point, Polygon, Feature, FeatureCollection


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    environment: str
    db_connection: str
    redis_connection: str


class ThreatLevel(str, Enum):
    """Enumeration of possible threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(str, Enum):
    """Types of biological threats to crops"""
    FUNGAL = "fungal"
    BACTERIAL = "bacterial"
    VIRAL = "viral"
    PEST = "pest"
    UNKNOWN = "unknown"
    BIOWEAPON = "bioweapon"


class SensorType(str, Enum):
    """Types of sensors for data collection"""
    SOIL = "soil"
    WEATHER = "weather"
    AERIAL = "aerial"
    CAMERA = "camera"
    SATELLITE = "satellite"


class SensorDataBase(BaseModel):
    """Base model for sensor data"""
    sensor_id: str = Field(..., description="Unique identifier for the sensor")
    timestamp: datetime = Field(..., description="Timestamp when the data was collected")
    location: Point = Field(..., description="GeoJSON Point representing the sensor location")
    sensor_type: SensorType = Field(..., description="Type of sensor")


class SoilSensorData(SensorDataBase):
    """Data model for soil sensors"""
    moisture: float = Field(..., description="Soil moisture percentage")
    ph: float = Field(..., description="Soil pH level")
    temperature: float = Field(..., description="Soil temperature in Celsius")
    nitrogen: Optional[float] = Field(None, description="Nitrogen level in soil")
    phosphorus: Optional[float] = Field(None, description="Phosphorus level in soil")
    potassium: Optional[float] = Field(None, description="Potassium level in soil")
    pathogen_indicators: Optional[Dict[str, float]] = Field(None, description="Indicators of potential pathogens")


class WeatherSensorData(SensorDataBase):
    """Data model for weather sensors"""
    temperature: float = Field(..., description="Air temperature in Celsius")
    humidity: float = Field(..., description="Air humidity percentage")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_direction: float = Field(..., description="Wind direction in degrees")
    precipitation: float = Field(..., description="Precipitation in mm")
    solar_radiation: Optional[float] = Field(None, description="Solar radiation in W/m²")


class ImageData(SensorDataBase):
    """Data model for image-based sensors (cameras, satellites)"""
    image_url: str = Field(..., description="URL to the image file")
    image_type: str = Field(..., description="Type of image (RGB, infrared, etc.)")
    resolution: str = Field(..., description="Image resolution")
    coverage_area: Polygon = Field(..., description="Area covered by the image")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional image metadata")


class SensorData(BaseModel):
    """Union model that can accept different types of sensor data"""
    data: Union[SoilSensorData, WeatherSensorData, ImageData]


class ThreatDetection(BaseModel):
    """Model for detected threats"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the threat")
    threat_type: ThreatType = Field(..., description="Type of biological threat")
    threat_level: ThreatLevel = Field(..., description="Severity level of the threat")
    detection_time: datetime = Field(default_factory=datetime.now, description="Time when the threat was detected")
    confidence: float = Field(..., description="Confidence level of the detection (0-1)")
    location: Point = Field(..., description="GeoJSON Point representing the threat location")
    affected_area: Optional[Polygon] = Field(None, description="GeoJSON Polygon of the potentially affected area")
    description: str = Field(..., description="Description of the detected threat")
    recommendations: List[str] = Field(default=[], description="Recommended actions to address the threat")
    source_data: List[str] = Field(..., description="References to source data used for detection")


class ThreatPrediction(ThreatDetection):
    """Model for predicted threat spread"""
    prediction_time: datetime = Field(..., description="Time for which the prediction is made")
    spread_velocity: Optional[float] = Field(None, description="Predicted spread velocity in m/day")
    spread_pattern: Optional[Dict[str, Any]] = Field(None, description="Pattern of predicted spread")
    probability: float = Field(..., description="Probability of the prediction being accurate (0-1)")


class AnalyticsRequest(BaseModel):
    """Request model for analytics data"""
    start_date: datetime = Field(..., description="Start date for the analysis")
    end_date: datetime = Field(..., description="End date for the analysis")
    area_of_interest: Optional[Polygon] = Field(None, description="GeoJSON Polygon of the area of interest")
    threat_types: Optional[List[ThreatType]] = Field(None, description="Types of threats to include in analysis")
    aggregation_level: Optional[str] = Field("day", description="Time aggregation level (hour, day, week, month)")


class AnalyticsResponse(BaseModel):
    """Response model for analytics data"""
    time_period: str = Field(..., description="Time period covered by the analysis")
    threat_counts: Dict[str, int] = Field(..., description="Count of threats by type")
    threat_levels: Dict[str, int] = Field(..., description="Count of threats by severity level")
    hotspots: List[Feature] = Field(..., description="GeoJSON Features representing threat hotspots")
    trends: Dict[str, List[float]] = Field(..., description="Trend data for different metrics")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    code: int
    details: Optional[Any] = None


class UserBase(BaseModel):
    """Base model for user data"""
    username: str
    email: str
    role: str


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str


class UserResponse(UserBase):
    """Model for user data in responses"""
    id: str
    created_at: datetime
