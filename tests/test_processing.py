import pytest
import numpy as np
import json
from unittest.mock import MagicMock, patch
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.processing.worker import ProcessingWorker
from src.processing.anomaly_detection import detect_anomalies, evaluate_threat_level
from src.processing.image_processing import analyze_crop_image
from src.processing.geospatial import map_threat_area, predict_spread


class TestProcessingPipeline:
    """Tests for the data processing pipeline."""
    
    def test_anomaly_detection(self):
        """Test that anomaly detection correctly identifies abnormal data."""
        # Normal range for soil data
        normal_data = {
            'moisture': 35.0,  # Within normal range
            'ph': 6.5,         # Neutral pH
            'temperature': 22.0,
            'nitrogen': 45.0,
            'phosphorus': 25.0,
            'potassium': 150.0
        }
        
        # Abnormal data with high moisture and acidic pH
        abnormal_data = {
            'moisture': 75.0,  # Very high moisture
            'ph': 4.5,         # Acidic
            'temperature': 22.0,
            'nitrogen': 45.0,
            'phosphorus': 25.0,
            'potassium': 150.0
        }
        
        # Test normal data
        anomalies_normal, confidence_normal = detect_anomalies(normal_data, sensor_type='soil')
        assert len(anomalies_normal) == 0  # No anomalies expected
        assert confidence_normal == 0.0    # No confidence in anomalies
        
        # Test abnormal data
        anomalies_abnormal, confidence_abnormal = detect_anomalies(abnormal_data, sensor_type='soil')
        assert len(anomalies_abnormal) > 0  # Anomalies expected
        assert confidence_abnormal > 0.5    # Reasonable confidence in anomalies
        assert any("moisture" in anomaly.lower() for anomaly in anomalies_abnormal)
        assert any("ph" in anomaly.lower() for anomaly in anomalies_abnormal)
    
    def test_threat_level_evaluation(self):
        """Test that threat level is correctly evaluated from anomalies."""
        # Test fungal threat evaluation
        fungal_anomalies = ["High moisture: 75.0 (normal range: 20.0-60.0)", 
                          "Low ph: 4.5 (normal range: 5.5-7.5)"]
        threat_type, threat_level = evaluate_threat_level(fungal_anomalies, 0.85, 'soil')
        
        assert threat_type == "FUNGAL"  # Should detect fungal threat based on moisture & pH
        assert threat_level in ["MEDIUM", "HIGH"]  # Should be at least medium severity
        
        # Test bacterial threat evaluation
        bacterial_anomalies = ["High temperature: 32.0 (normal range: 10.0-30.0)",
                             "High moisture: 65.0 (normal range: 20.0-60.0)"]
        threat_type, threat_level = evaluate_threat_level(bacterial_anomalies, 0.7, 'soil')
        
        assert threat_type == "BACTERIAL"  # Should detect bacterial threat
        assert threat_level in ["LOW", "MEDIUM", "HIGH"]  # Some level of severity
    
    def test_image_processing(self):
        """Test image processing for disease detection."""
        # Mock the image analysis function to avoid actual image download
        with patch('src.processing.image_processing.download_image') as mock_download:
            # Create a simple test image with a pattern that looks like a fungal infection
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            # Add some "fungal spots" to the image
            for i in range(30, 70):
                for j in range(30, 70):
                    if (i - 50)**2 + (j - 50)**2 < 100:  # Circular pattern
                        test_image[i, j] = [70, 50, 40]  # Brown-ish color
            
            mock_download.return_value = test_image
            
            # Test image analysis
            result = analyze_crop_image("dummy_url", image_type="RGB")
            
            # Check that something was detected
            assert result is not None
            assert "disease_type" in result
            assert "confidence" in result
            assert result["confidence"] > 0.3  # Some minimal confidence
            assert "recommendations" in result
            assert len(result["recommendations"]) > 0
    
    def test_geospatial_analysis(self):
        """Test geospatial analysis for mapping threat areas."""
        # Test threat area mapping
        location = {"type": "Point", "coordinates": [-97.7431, 30.2672]}
        affected_area = map_threat_area(location, "FUNGAL", "test-sensor", radius_meters=100)
        
        assert affected_area is not None
        assert affected_area["type"] == "Polygon"
        assert "coordinates" in affected_area
        assert len(affected_area["coordinates"]) > 0  # Has some coordinates
        
        # Test spread prediction
        predictions = predict_spread(
            threat_id="test-threat",
            threat_type="FUNGAL",
            location=location,
            detection_time=datetime.now().isoformat(),
            days_to_predict=3
        )
        
        assert len(predictions) == 3  # One prediction per day
        assert "threat_level" in predictions[0]
        assert "confidence" in predictions[0]
        assert "probability" in predictions[0]
        assert "affected_area" in predictions[0]
        
        # Check that predictions change over time (spread increases)
        area_day1 = predictions[0]["affected_area"]
        area_day3 = predictions[2]["affected_area"]
        coords_day1 = area_day1["coordinates"][0]
        coords_day3 = area_day3["coordinates"][0]
        
        # Area on day 3 should be larger than day 1
        assert len(coords_day3) >= len(coords_day1)
    
    def test_worker_processing(self):
        """Test the main processing worker."""
        # Create a mock Redis client and DB connection
        redis_mock = MagicMock()
        db_conn_mock = MagicMock()
        
        # Configure Redis mock to return soil data when queried
        soil_data = {
            "sensor_id": "sensor-001",
            "timestamp": "2025-04-26T15:30:45Z",
            "location": {"type": "Point", "coordinates": [-97.7431, 30.2672]},
            "sensor_type": "soil",
            "moisture": 75.0,
            "ph": 4.5,
            "temperature": 22.0
        }
        redis_mock.lpop.return_value = json.dumps(soil_data)
        
        # Create a worker with mocked connections
        worker = ProcessingWorker()
        worker.redis_client = redis_mock
        worker.db_conn = db_conn_mock
        
        # Test processing soil data
        detection = worker.process_soil_data(soil_data)
        
        # Verify a threat was detected
        assert detection is not None
        assert "threat_type" in detection
        assert detection["threat_type"] in ["FUNGAL", "BACTERIAL"]  # Most likely types for this data
        assert "threat_level" in detection
        assert "confidence" in detection
        assert "recommendations" in detection
        assert len(detection["recommendations"]) > 0
    
    def test_bioterrorism_scenario(self, bioterrorism_scenario_data):
        """Test system's response to a simulated bioterrorism scenario."""
        # Extract just the data part from the fixture
        scenario_data = bioterrorism_scenario_data["data"]
        
        # Create a worker instance
        worker = ProcessingWorker()
        
        # Process the suspicious data
        detection = worker.process_soil_data(scenario_data)
        
        # Assert that a severe threat was detected
        assert detection is not None
        assert detection["threat_type"] == "BIOWEAPON"  # Should identify as potential bioweapon
        assert detection["threat_level"] in ["HIGH", "CRITICAL"]  # Should be high severity
        assert detection["confidence"] > 0.8  # High confidence
        
        # Check for appropriate recommendations
        recommendations = detection["recommendations"]
        assert any("authorities" in r.lower() for r in recommendations)
        assert any("restrict" in r.lower() for r in recommendations)
        assert any("not attempt" in r.lower() for r in recommendations)  # Should advise not to attempt remediation
        
        # Also check that an affected area was mapped
        assert "affected_area" in detection
        assert detection["affected_area"] is not None


if __name__ == "__main__":
    pytest.main()

