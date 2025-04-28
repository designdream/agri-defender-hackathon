import os
import sys
import pytest
import numpy as np
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.models import SensorData, SoilSensorData, ThreatDetection, ThreatType, ThreatLevel
from src.models.spread_prediction import PathogenSpreadModel
from src.models.data_generator import generate_initial_state, generate_synthetic_dataset


@pytest.fixture
def api_client():
    """
    Create a test client for the FastAPI application.
    
    Returns:
        TestClient: A test client for the FastAPI application
    """
    from fastapi.testclient import TestClient
    from src.api.main import app
    
    return TestClient(app)


@pytest.fixture
def sample_sensor_data():
    """
    Generate sample sensor data for testing.
    
    Returns:
        dict: Sample sensor data
    """
    return {
        "data": {
            "sensor_id": "sensor-001",
            "timestamp": datetime.now().isoformat(),
            "location": {
                "type": "Point",
                "coordinates": [-97.7431, 30.2672]
            },
            "sensor_type": "SOIL",
            "moisture": 78.5,  # Abnormally high moisture
            "ph": 5.2,          # Slightly acidic
            "temperature": 27.3,
            "nitrogen": 45.2,
            "phosphorus": 22.8,
            "potassium": 120.6
        }
    }


@pytest.fixture
def sample_weather_data():
    """
    Generate sample weather sensor data for testing.
    
    Returns:
        dict: Sample weather data
    """
    return {
        "data": {
            "sensor_id": "weather-001",
            "timestamp": datetime.now().isoformat(),
            "location": {
                "type": "Point",
                "coordinates": [-97.7431, 30.2672]
            },
            "sensor_type": "WEATHER",
            "temperature": 32.5,  # High temperature
            "humidity": 85.0,     # High humidity
            "wind_speed": 15.2,
            "wind_direction": 180.0,
            "precipitation": 0.0
        }
    }


@pytest.fixture
def sample_image_data():
    """
    Generate sample image data for testing.
    
    Returns:
        dict: Sample image data
    """
    return {
        "data": {
            "sensor_id": "camera-001",
            "timestamp": datetime.now().isoformat(),
            "location": {
                "type": "Point",
                "coordinates": [-97.7431, 30.2672]
            },
            "sensor_type": "CAMERA",
            "image_url": "https://example.com/sample-crop-image.jpg",
            "image_type": "RGB",
            "resolution": "1920x1080",
            "coverage_area": {
                "type": "Polygon",
                "coordinates": [[
                    [-97.7531, 30.2572],
                    [-97.7331, 30.2572],
                    [-97.7331, 30.2772],
                    [-97.7531, 30.2772],
                    [-97.7531, 30.2572]
                ]]
            },
            "metadata": {
                "camera_height": 2.5,
                "field_id": "field-112",
                "crop_type": "corn"
            }
        }
    }


@pytest.fixture
def sample_threat_data():
    """
    Generate sample threat data for testing.
    
    Returns:
        dict: Sample threat data
    """
    return {
        "id": "threat-100",
        "threat_type": "FUNGAL",
        "threat_level": "HIGH",
        "detection_time": datetime.now().isoformat(),
        "confidence": 0.87,
        "location": {
            "type": "Point",
            "coordinates": [-97.7431, 30.2672]
        },
        "description": "Fungal pathogen detected in soil samples with high moisture conditions",
        "recommendations": [
            "Apply fungicide treatment to affected area",
            "Improve drainage to reduce soil moisture",
            "Monitor surrounding areas for signs of spread"
        ],
        "source_data": ["sensor-001", "satellite-001"]
    }


@pytest.fixture
def bioterrorism_scenario_data():
    """
    Generate data for a simulated bioterrorism scenario.
    
    Returns:
        dict: Bioterrorism scenario data
    """
    # Simulated intentional introduction of a dangerous pathogen
    return {
        "data": {
            "sensor_id": "sensor-b52",
            "timestamp": datetime.now().isoformat(),
            "location": {
                "type": "Point",
                "coordinates": [-97.7431, 30.2672]
            },
            "sensor_type": "SOIL",
            "moisture": 65.0,
            "ph": 4.8,  # Very acidic, unusual for normal agriculture
            "temperature": 29.8,
            "nitrogen": 150.3,  # Extremely high nitrogen
            "phosphorus": 98.5,  # Unusual chemical composition
            "potassium": 210.2,
            "pathogen_indicators": {
                "unidentified_organism": 0.92,  # Very high confidence of unknown pathogen
                "unusual_enzyme_activity": 0.85,
                "toxin_markers": 0.78
            }
        }
    }


@pytest.fixture
def mock_database_session():
    """
    Create a mock database session for testing.
    
    Returns:
        MagicMock: A mock database session
    """
    session = MagicMock()
    
    # Mock query results for threats
    mock_threats = [
        ThreatDetection(
            id="threat-101",
            threat_type=ThreatType.FUNGAL,
            threat_level=ThreatLevel.MEDIUM,
            detection_time=datetime.now() - timedelta(days=1),
            confidence=0.82,
            location={"type": "Point", "coordinates": [-97.7431, 30.2672]},
            description="Fungal infection detected in wheat field",
            recommendations=["Apply fungicide", "Monitor spread"],
            source_data=["sensor-001"]
        ),
        ThreatDetection(
            id="threat-102",
            threat_type=ThreatType.BACTERIAL,
            threat_level=ThreatLevel.HIGH,
            detection_time=datetime.now() - timedelta(hours=12),
            confidence=0.91,
            location={"type": "Point", "coordinates": [-97.7631, 30.2472]},
            description="Bacterial blight detected in rice paddy",
            recommendations=["Apply bactericide", "Isolate affected area"],
            source_data=["sensor-002"]
        )
    ]
    
    # Configure session mock to return predefined threats
    session.query.return_value.filter.return_value.all.return_value = mock_threats
    session.query.return_value.get.return_value = mock_threats[0]
    
    return session


@pytest.fixture
def trained_test_model():
    """
    Create a small trained model for testing purposes.
    
    Returns:
        PathogenSpreadModel: A trained model instance
    """
    # Generate a very small synthetic dataset
    spatial_dim = 16  # Small spatial dimension for testing
    time_steps = 3    # Few time steps for faster training
    features = 5
    
    X, y = generate_synthetic_dataset(
        dataset_size=50,  # Small dataset for testing
        spatial_dim=spatial_dim,
        time_steps=time_steps,
        features=features
    )
    
    # Split into train and validation sets
    X_train, X_val = X[:40], X[40:]
    y_train, y_val = y[:40], y[40:]
    
    # Create model with small capacity for fast testing
    model = PathogenSpreadModel(
        spatial_dim=spatial_dim,
        time_steps=time_steps,
        features=features,
        lstm_units=16  # Small LSTM for faster training
    )
    
    # Train for just a few epochs
    model.train(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        epochs=2,  # Just enough to get a working model
        batch_size=8,
        patience=1
    )
    
    return model


@pytest.fixture
def temp_model_dir():
    """
    Create a temporary directory for model files.
    
    Yields:
        str: Path to the temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_processing_data():
    """
    Generate sample data for the processing pipeline.
    
    Returns:
        tuple: Sample input and expected output data
    """
    # Generate a simple initial state
    initial_state = generate_initial_state(
        spatial_dim=32,
        features=5,
        concentration=0.7,
        num_points=1,
        random_seed=42
    )
    
    # Create expected outputs (simplified for testing)
    expected_detection = {
        'threat_type': 'FUNGAL',
        'threat_level': 'MEDIUM',
        'confidence': 0.75,
    }
    
    return initial_state, expected_detection


@pytest.fixture
def redis_mock():
    """
    Create a mock Redis client for testing.
    
    Returns:
        MagicMock: A mock Redis client
    """
    redis_client = MagicMock()
    
    # Configure mock to return some example sensor data
    redis_client.lpop.return_value = json.dumps({
        "sensor_id": "sensor-001",
        "timestamp": datetime.now().isoformat(),
        "location": {
            "type": "Point",
            "coordinates": [-97.7431, 30.2672]
        },
        "sensor_type": "SOIL",
        "moisture": 75.0,
        "ph": 5.5,
        "temperature": 25.0
    })
    
    return redis_client


@pytest.fixture
def mock_ml_model():
    """
    Create a mock machine learning model for testing.
    
    Returns:
        MagicMock: A mock model
    """
    model = MagicMock()
    
    # Mock predict method to return a simple prediction
    def mock_predict(X):
        batch_size = X.shape[0]
        spatial_dim = X.shape[2]
        features = X.shape[4]
        
        # Return a simple prediction with values between 0 and 1
        return np.random.random((batch_size, spatial_dim, spatial_dim, features))
    
    model.predict.side_effect = mock_predict
    
    return model

import os
import sys
import pytest
import numpy as np
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.models import SensorData, SoilSensorData, ThreatDetection, ThreatType, ThreatLevel
from src.models.spread_prediction import PathogenSpreadModel
from src.models.data_generator import generate_initial_state, generate_synthetic_dataset


@pytest.fixture
def api_client():
    """
    Create a test client for the FastAPI application.
    
    Returns:
        TestClient: A test client for the FastAPI application
    """
    from fastapi.testclient import TestClient
    from src.api.main import app
    
    return TestClient(app)


@pytest.fixture
def sample_sensor_data():
    """
    Generate sample sensor data for testing.
    
    Returns:
        dict: Sample sensor data
    """
    return {
        "data": {
            "sensor_id": "sensor-001",
            "timestamp": datetime.now().isoformat(),
            "location": {
                "type": "Point",
                "coordinates": [-97.7431, 30.2672]
            },
            "sensor_type": "SOIL",
            "moisture": 78.5,  # Abnormally high moisture
            "ph": 5.2,          # Slightly acidic
            "temperature": 27.3,
            "nitrogen": 45.2,
            "phosphorus": 22.8,
            "potassium": 120.6
        }
    }


@pytest.fixture
def sample_threat_data():
    """
    Generate sample threat data for testing.
    
    Returns:
        dict: Sample threat data
    """
    return {
        "id": "threat-100",
        "threat_type": "FUNGAL",
        "threat_level": "HIGH",
        "detection_time": datetime.now().isoformat(),
        "confidence": 0.87,
        "location": {
            "type": "Point",
            "coordinates": [-97.7431, 30.2672]
        },
        "description": "Fungal pathogen detected in soil samples with high moisture conditions",
        "recommendations": [
            "Apply fungicide treatment to affected area",
            "Improve drainage to reduce soil moisture",
            "Monitor surrounding areas for signs of spread"
        ],
        "source_data": ["sensor-001", "satellite-001"]
    }


@pytest.fixture
def bioterrorism_scenario_data():
    """
    Generate data for a simulated bioterrorism scenario.
    
    Returns:
        dict: Bioterrorism scenario data
    """
    # Simulated intentional introduction of a dangerous pathogen
    return {
        "data": {
            "sensor_id": "sensor-b52",
            "timestamp": datetime.now().isoformat(),
            "location": {
                "type": "Point",
                "coordinates": [-97.7431, 30.2672]
            },
            "sensor_type": "SOIL",
            "moisture": 65.0,
            "ph": 4.8,  # Very acidic, unusual for normal agriculture
            "temperature": 29.8,
            "nitrogen": 150.3,  # Extremely high nitrogen
            "phosphorus": 98.5,  # Unusual chemical composition
            "potassium": 210.2,
            "pathogen_indicators": {
                "unidentified_organism": 0.92,  # Very high confidence of unknown pathogen
                "unusual_enzyme_activity": 0.85,
                "toxin_markers": 0.78
            }
        }
    }


@pytest.fixture
def mock_database_session():
    """
    Create a mock database session for testing.
    
    Returns:
        MagicMock: A mock database session
    """
    session = MagicMock()
    
    # Mock query results for threats
    mock_threats = [
        ThreatDetection(
            id="threat-101",
            threat_type=ThreatType.FUNGAL,
            threat_level=ThreatLevel.MEDIUM,
            detection_time=datetime.now() - timedelta(days=1),
            confidence=0.82,
            location={"type": "Point", "coordinates": [-97.7431, 30.2672]},
            description="Fungal infection detected in wheat field",
            recommendations=["Apply fungicide", "Monitor spread"],
            source_data=["sensor-001"]
        ),
        ThreatDetection(
            id="threat-102",
            threat_type=ThreatType.BACTERIAL,
            threat_level=ThreatLevel.HIGH,
            detection_time=datetime.now() - timedelta(hours=12),
            confidence=0.91,
            location={"type": "Point", "coordinates": [-97.7631, 30.2472]},
            description="Bacterial blight detected in rice paddy",
            recommendations=["Apply bactericide", "Isolate affected area"],
            source_data=["sensor-002"]
        )
    ]
    
    # Configure session mock to return predefined threats
    session.query.return_value.filter.return_value.all.return_value = mock_threats
    session.query.return_value.get.return_value = mock_threats[0]
    
    return session


@pytest.fixture
def trained_test_model():
    """
    Create a small trained model for testing purposes.
    
    Returns:
        PathogenSpreadModel: A trained model instance
    """
    # Generate a very small synthetic dataset
    spatial_dim = 16  # Small spatial dimension for testing
    time_steps = 3    # Few time steps for faster training
    features = 5
    
    X, y = generate_synthetic_dataset(
        dataset_size=50,  # Small dataset for testing
        spatial_dim=spatial_dim,
        time_steps=time_steps,
        features=features
    )
    
    # Split into train and validation sets
    X_train, X_val = X[:40], X[40:]
    y_train, y_val = y[:40], y[40:]
    
    # Create model with small capacity for fast testing
    model = PathogenSpreadModel(
        spatial_dim=spatial_dim,
        time_steps=time_steps,
        features=features,
        lstm_units=16  # Small LSTM for faster training
    )
    
    # Train for just a few epochs
    model.train(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        epochs=2,  # Just enough to get a working model
        batch_size=8,
        patience=1
    )
    
    return model


@pytest.fixture
def temp_model_dir():
    """
    Create a temporary directory for model files.
    
    Yields:
        str: Path to the temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_processing_data():
    """
    Generate sample data for the processing pipeline.
    
    Returns:
        tuple: Sample input and expected output data
    """
    # Generate a simple initial state
    initial_state = generate_initial_state(
        spatial_dim=32,
        features=5,
        concentration=0.7,
        num_points=1,
        random_seed=42
    )
    
    # Create expected outputs (simplified for testing)
    expected_detection = {
        'threat_type': 'FUNGAL',
        'threat_level': 'MEDIUM',
        'confidence': 0.75,
    }
    
    return initial_state, expected_detection


@pytest.fixture
def redis_mock():
    """
    Create a mock Redis client for testing.
    
    Returns:
        MagicMock: A mock Redis client
    """
    redis_client = MagicMock()
    
    # Configure mock to return some example sensor data
    redis_client.lpop.return_value = json.dumps({
        "sensor_id": "sensor-001",
        "timestamp": datetime.now().isoformat(),
        "location": {
            "type": "Point",
            "coordinates": [-97.7431, 30.2672]
        },
        "sensor_type": "SOIL",
        "moisture": 75.0,
        "ph": 5.5,
        "temperature": 25.0
    })
    
    return redis_client

