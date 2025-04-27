import pytest
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from src.api.models import ThreatType, ThreatLevel


class TestAPIEndpoints:
    """Tests for the API endpoints."""
    
    def test_health_check(self, api_client):
        """Test the health check endpoint returns expected response."""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data
    
    def test_root_endpoint(self, api_client):
        """Test the root endpoint provides basic information."""
        response = api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "AgriDefender" in data["message"]
    
    def test_submit_sensor_data(self, api_client, sample_sensor_data):
        """Test submitting sensor data."""
        response = api_client.post(
            "/api/v1/sensors/data",
            json=sample_sensor_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
    
    def test_get_sensor_data(self, api_client):
        """Test retrieving sensor data with filters."""
        response = api_client.get(
            "/api/v1/sensors/data",
            params={"sensor_type": "SOIL", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Assuming mock data is returned for this test
        if data:
            assert "sensor_id" in data[0]
            assert "sensor_type" in data[0]
    
    def test_get_sensor_stats(self, api_client):
        """Test retrieving sensor statistics."""
        response = api_client.get("/api/v1/sensors/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_sensors" in data
        assert "active_sensors" in data
        assert "by_type" in data
    
    def test_register_sensor(self, api_client):
        """Test registering a new sensor."""
        sensor_info = {
            "name": "Test Sensor",
            "type": "SOIL",
            "location": {
                "type": "Point",
                "coordinates": [-97.7431, 30.2672]
            }
        }
        response = api_client.post(
            "/api/v1/sensors/register",
            json=sensor_info
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "sensor_id" in data
    
    def test_get_threats(self, api_client):
        """Test retrieving threats with filters."""
        response = api_client.get(
            "/api/v1/threats/",
            params={
                "threat_type": "FUNGAL",
                "threat_level": "MEDIUM,HIGH"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "id" in data[0]
            assert "threat_type" in data[0]
            assert "threat_level" in data[0]
    
    def test_get_threat_by_id(self, api_client):
        """Test retrieving a specific threat by ID."""
        # Assuming a threat with ID "threat-101" exists in mock data
        response = api_client.get("/api/v1/threats/threat-101")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "threat-101"
        assert "threat_type" in data
        assert "threat_level" in data
    
    def test_get_threat_predictions(self, api_client):
        """Test retrieving predictions for a threat."""
        # Assuming a threat with ID "threat-101" exists in mock data
        response = api_client.get(
            "/api/v1/threats/threat-101/predictions",
            params={"time_horizon": 7}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            # Check that predictions are for future days
            assert "prediction_time" in data[0]
            assert "threat_level" in data[0]
            assert "probability" in data[0]
    
    def test_report_threat(self, api_client):
        """Test reporting a new threat."""
        threat_info = {
            "threat_type": "BACTERIAL",
            "description": "Unusual bacterial growth observed in field",
            "location": {
                "type": "Point",
                "coordinates": [-97.7531, 30.2772]
            },
            "observations": [
                "Yellow discoloration on leaves",
                "Wilting plants",
                "Wet soil conditions"
            ]
        }
        response = api_client.post(
            "/api/v1/threats/report",
            json=threat_info
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "threat_id" in data
    
    def test_get_analytics(self, api_client):
        """Test retrieving analytics data."""
        analytics_request = {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "aggregation_level": "day"
        }
        response = api_client.post(
            "/api/v1/analytics/",
            json=analytics_request
        )
        assert response.status_code == 200
        data = response.json()
        assert "time_period" in data
        assert "threat_counts" in data
        assert "threat_levels" in data
        assert "hotspots" in data
        assert "trends" in data
    
    def test_get_summary_statistics(self, api_client):
        """Test retrieving summary statistics."""
        response = api_client.get(
            "/api/v1/analytics/summary",
            params={"days": 30}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_threats_detected" in data
        assert "threats_by_type" in data
        assert "average_detection_confidence" in data
        assert "most_affected_regions" in data
    
    def test_export_analytics(self, api_client):
        """Test exporting analytics data."""
        response = api_client.get(
            "/api/v1/analytics/export",
            params={
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "format": "csv"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "export_id" in data
        assert "download_url" in data
    
    def test_system_status(self, api_client):
        """Test admin endpoint for system status."""
        response = api_client.get("/api/v1/admin/system/status")
        assert response.status_code == 200
        data = response.json()
        assert "api" in data
        assert "database" in data
        assert "processing" in data
        assert "models" in data
    
    def test_bioterrorism_scenario(self, api_client, bioterrorism_scenario_data):
        """Test system's response to a simulated bioterrorism scenario."""
        # First, submit the suspicious sensor data
        response = api_client.post(
            "/api/v1/sensors/data",
            json=bioterrorism_scenario_data
        )
        assert response.status_code == 201
        
        # Then check if a high-severity threat was created
        response = api_client.get(
            "/api/v1/threats/",
            params={"threat_level": "HIGH,CRITICAL"}
        )
        assert response.status_code == 200
        threats = response.json()
        
        # Verify a bioweapon threat was detected
        bioweapon_threats = [t for t in threats if t.get("threat_type") == "BIOWEAPON"]
        assert len(bioweapon_threats) > 0
        
        if bioweapon_threats:
            # Check that the threat has appropriate recommendations
            threat = bioweapon_threats[0]
            recommendations = threat.get("recommendations", [])
            assert any("authorities" in r.lower() for r in recommendations)
            assert any("restrict" in r.lower() for r in recommendations)
            
            # Check confidence level is high
            assert threat.get("confidence", 0) > 0.8

