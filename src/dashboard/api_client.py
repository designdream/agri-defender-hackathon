import requests
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class AgriDefenderAPI:
    """Client for communicating with the AgriDefender API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client with the base URL."""
        self.base_url = base_url.rstrip("/")
        logger.info(f"Initialized API client with base URL: {self.base_url}")
    
    def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Make a request to the API.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Data to send in the request body
            
        Returns:
            Response data or None if the request failed
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, params=params, json=data, timeout=10)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            # For this demo, return mock data if API fails
            return self._get_mock_data(endpoint, params)
    
    def _get_mock_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Generate mock data for demonstrations when the API is unavailable.
        
        Args:
            endpoint: API endpoint that was called
            params: Query parameters that were used
            
        Returns:
            Mock data appropriate for the endpoint
        """
        logger.warning(f"Using mock data for endpoint: {endpoint}")
        
        if endpoint.startswith("/api/v1/threats"):
            # If it's a specific threat ID
            if "/predictions" in endpoint:
                return self._mock_threat_predictions()
            elif endpoint.count("/") > 2:  # Pattern like /api/v1/threats/{id}
                return self._mock_threat_detail()
            else:
                return self._mock_threats_list()
        
        elif endpoint.startswith("/api/v1/analytics"):
            if endpoint.endswith("/summary"):
                return self._mock_summary_statistics()
            else:
                return self._mock_analytics()
        
        # Default mock data
        return {}
    
    def get_threats(
        self,
        threat_id: Optional[str] = None,
        threat_types: Optional[List[str]] = None,
        severity_levels: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get threats from the API.
        
        Args:
            threat_id: Optional ID of a specific threat
            threat_types: Optional list of threat types to filter by
            severity_levels: Optional list of severity levels to filter by
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering
            limit: Maximum number of threats to return
            
        Returns:
            List of threat data
        """
        params = {}
        
        if threat_types:
            params["threat_type"] = ",".join(threat_types)
        
        if severity_levels:
            params["threat_level"] = ",".join(severity_levels)
        
        if start_time:
            params["start_time"] = start_time
        
        if end_time:
            params["end_time"] = end_time
        
        if limit:
            params["limit"] = str(limit)
        
        if threat_id:
            endpoint = f"/api/v1/threats/{threat_id}"
            result = self._make_request(endpoint)
            return [result] if result else []
        else:
            endpoint = "/api/v1/threats"
            return self._make_request(endpoint, params=params) or []
    
    def get_threat_predictions(
        self,
        threat_id: str,
        time_horizon: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get predictions for a specific threat.
        
        Args:
            threat_id: ID of the threat
            time_horizon: Number of days to predict ahead
            
        Returns:
            List of prediction data points
        """
        endpoint = f"/api/v1/threats/{threat_id}/predictions"
        params = {"time_horizon": str(time_horizon)}
        
        return self._make_request(endpoint, params=params) or []
    
    def get_analytics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        threat_types: Optional[List[str]] = None,
        aggregation_level: str = "day"
    ) -> Dict[str, Any]:
        """
        Get analytics data from the API.
        
        Args:
            start_date: Optional start date for the analysis
            end_date: Optional end date for the analysis
            threat_types: Optional list of threat types to include
            aggregation_level: Time aggregation level (hour, day, week, month)
            
        Returns:
            Analytics data
        """
        endpoint = "/api/v1/analytics"
        
        # Create request body
        data = {
            "start_date": start_date or (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": end_date or datetime.now().isoformat(),
            "aggregation_level": aggregation_level
        }
        
        if threat_types:
            data["threat_types"] = threat_types
        
        return self._make_request(endpoint, method="POST", data=data) or {}
    
    def get_summary_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get summary statistics for the dashboard.
        
        Args:
            days: Number of days to include in the summary
            
        Returns:
            Summary statistics data
        """
        endpoint = "/api/v1/analytics/summary"
        params = {"days": str(days)}
        
        return self._make_request(endpoint, params=params) or {}
    
    # Mock data methods for demonstration
    def _mock_threats_list(self) -> List[Dict[str, Any]]:
        """Generate mock threat list data for demonstrations."""
        threats = []
        
        threat_types = ["FUNGAL", "BACTERIAL", "VIRAL", "PEST", "UNKNOWN"]
        threat_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        descriptions = [
            "Fungal leaf spot detected in corn field",
            "Bacterial blight detected in rice paddy",
            "Possible viral infection in wheat field",
            "Corn borer infestation detected",
            "Unknown pathogen detected in soybean field"
        ]
        
        # Generate some mock threats
        for i in range(10):
            threat_type = threat_types[i % len(threat_types)]
            threat_level = threat_levels[i % len(threat_levels)]
            
            # Make higher indexes have more severe threats
            if i > 7:
                threat_level = "CRITICAL"
            elif i > 5:
                threat_level = "HIGH"
            
            # Create mock threat
            threat = {
                "id": f"threat-{100 + i}",
                "threat_type": threat_type,
                "threat_level": threat_level,
                "detection_time": (datetime.now() - timedelta(days=i)).isoformat(),
                "confidence": 0.75 + (i * 0.02) if i < 5 else 0.85,
                "location": {
                    "type": "Point",
                    "coordinates": [-97.7431 + (i * 0.05), 30.2672 + (i * 0.02)]
                },
                "description": descriptions[i % len(descriptions)],
                "recommendations": [
                    "Inspect affected area immediately",
                    "Collect samples for laboratory analysis",
                    "Consider applying appropriate treatment"
                ],
                "source_data": [
                    f"sensor-{200 + i}",
                    f"image-{300 + i}"
                ]
            }
            
            # Add affected area for some threats
            # Add affected area for some threats
            if i % 3 == 0:
                threat["affected_area"] = {
                    "type": "Polygon",
                    "coordinates": [[
                        [threat["location"]["coordinates"][0] - 0.01, threat["location"]["coordinates"][1] - 0.01],
                        [threat["location"]["coordinates"][0] + 0.01, threat["location"]["coordinates"][1] - 0.01],
                        [threat["location"]["coordinates"][0] + 0.01, threat["location"]["coordinates"][1] + 0.01],
                        [threat["location"]["coordinates"][0] - 0.01, threat["location"]["coordinates"][1] + 0.01],
                        [threat["location"]["coordinates"][0] - 0.01, threat["location"]["coordinates"][1] - 0.01]
                    ]]
                }
            
            threats.append(threat)
        
        return threats
    
    def _mock_threat_detail(self) -> Dict[str, Any]:
        """Generate mock detailed threat data for demonstrations."""
        # Generate a single detailed threat
        return {
            "id": "threat-105",
            "threat_type": "FUNGAL",
            "threat_level": "HIGH",
            "detection_time": (datetime.now() - timedelta(hours=12)).isoformat(),
            "confidence": 0.89,
            "location": {
                "type": "Point",
                "coordinates": [-97.7431, 30.2672]
            },
            "affected_area": {
                "type": "Polygon",
                "coordinates": [[
                    [-97.7531, 30.2572],
                    [-97.7331, 30.2572],
                    [-97.7331, 30.2772],
                    [-97.7531, 30.2772],
                    [-97.7531, 30.2572]
                ]]
            },
            "description": "Fungal leaf spot detected in corn field with high severity",
            "recommendations": [
                "Inspect affected area immediately",
                "Apply fungicide treatment to affected and surrounding areas",
                "Monitor closely for the next 48 hours",
                "Collect samples for laboratory analysis"
            ],
            "source_data": [
                "sensor-205",
                "image-305",
                "field-report-105"
            ]
        }
    
    def _mock_threat_predictions(self) -> List[Dict[str, Any]]:
        """Generate mock threat prediction data for demonstrations."""
        predictions = []
        
        # Base location
        base_lon, base_lat = -97.7431, 30.2672
        base_detection_time = datetime.now() - timedelta(days=1)
        
        # Generate predictions for 7 days
        for day in range(1, 8):
            # Predictions get less confident over time
            confidence = max(0.4, 0.9 - (day * 0.05))
            probability = max(0.3, 0.85 - (day * 0.07))
            
            # Severity increases over time if unchecked
            severity = "LOW"
            if day > 2:
                severity = "MEDIUM"
            if day > 4:
                severity = "HIGH"
            if day > 6:
                severity = "CRITICAL"
            
            # Spread increases over time (simulating movement and growth)
            spread_distance = 5.0 * day
            
            # Location shifts slightly to simulate spread direction
            pred_lon = base_lon + (0.005 * day)
            pred_lat = base_lat + (0.003 * day)
            
            # Create the prediction object
            prediction = {
                "threat_id": "threat-105",
                "prediction_time": (base_detection_time + timedelta(days=day)).isoformat(),
                "threat_level": severity,
                "confidence": confidence,
                "probability": probability,
                "location": {
                    "type": "Point",
                    "coordinates": [pred_lon, pred_lat]
                },
                "affected_area": {
                    "type": "Polygon",
                    "coordinates": [[
                        [pred_lon - 0.01 * day, pred_lat - 0.01 * day],
                        [pred_lon + 0.01 * day, pred_lat - 0.01 * day],
                        [pred_lon + 0.01 * day, pred_lat + 0.01 * day],
                        [pred_lon - 0.01 * day, pred_lat + 0.01 * day],
                        [pred_lon - 0.01 * day, pred_lat - 0.01 * day]
                    ]]
                },
                "spread_velocity": 5.0 + (day * 0.5),
                "day": day
            }
            
            predictions.append(prediction)
        
        return predictions
    
    def _mock_analytics(self) -> Dict[str, Any]:
        """Generate mock analytics data for demonstrations."""
        return {
            "time_period": f"{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
            "threat_counts": {
                "fungal": 28,
                "bacterial": 12,
                "viral": 5,
                "pest": 35,
                "unknown": 7
            },
            "threat_levels": {
                "low": 42,
                "medium": 30,
                "high": 12,
                "critical": 3
            },
            "hotspots": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-97.733330, 30.266666]
                    },
                    "properties": {
                        "intensity": 0.85,
                        "threat_count": 15,
                        "region": "Central Texas"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-95.369804, 29.760427]
                    },
                    "properties": {
                        "intensity": 0.72,
                        "threat_count": 9,
                        "region": "Southeast Texas"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-99.901813, 31.968599]
                    },
                    "properties": {
                        "intensity": 0.58,
                        "threat_count": 6,
                        "region": "West Texas"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-96.797401, 32.776665]
                    },
                    "properties": {
                        "intensity": 0.67,
                        "threat_count": 8,
                        "region": "North Texas"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-97.501144, 27.525572]
                    },
                    "properties": {
                        "intensity": 0.75,
                        "threat_count": 12,
                        "region": "South Texas"
                    }
                }
            ],
            "trends": {
                "fungal_infections": [3, 5, 7, 8, 5],
                "bacterial_incidents": [2, 4, 3, 2, 1],
                "detection_confidence": [0.82, 0.85, 0.87, 0.89, 0.92]
            }
        }
    
    def _mock_summary_statistics(self) -> Dict[str, Any]:
        """Generate mock summary statistics for demonstrations."""
        return {
            "total_threats_detected": 87,
            "threats_by_type": {
                "fungal": 28,
                "bacterial": 12,
                "viral": 5,
                "pest": 35,
                "unknown": 7
            },
            "average_detection_confidence": 0.87,
            "most_affected_regions": [
                {"name": "Central Texas", "threat_count": 25},
                {"name": "Southeast Texas", "threat_count": 18},
                {"name": "West Texas", "threat_count": 12},
                {"name": "North Texas", "threat_count": 15},
                {"name": "South Texas", "threat_count": 17}
            ],
            "trends": {
                "detection_rate": "increasing",
                "false_positive_rate": "decreasing",
                "affected_area": "stable"
            }
        }
