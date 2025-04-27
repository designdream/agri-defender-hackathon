import logging
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Define normal ranges for different sensor types
NORMAL_RANGES = {
    'soil': {
        'moisture': (20.0, 60.0),  # Percentage
        'ph': (5.5, 7.5),          # pH scale
        'temperature': (10.0, 35.0),  # Celsius
        'nitrogen': (20.0, 80.0),   # ppm
        'phosphorus': (10.0, 50.0), # ppm
        'potassium': (75.0, 250.0)  # ppm
    },
    'weather': {
        'temperature': (5.0, 35.0),   # Celsius
        'humidity': (30.0, 80.0),     # Percentage
        'precipitation': (0.0, 25.0), # mm
        'wind_speed': (0.0, 30.0),    # m/s
        'wind_direction': (0.0, 360.0)  # degrees
    }
}

# Define conditions favorable for specific threats
FAVORABLE_CONDITIONS = {
    'FUNGAL': {
        'soil': {
            'moisture': ('>55', 'High soil moisture favorable for fungal growth'),
            'ph': ('<6.0', 'Acidic soil conditions favor certain fungi'),
            'temperature': ('range:15-30', 'Optimal temperature range for fungal growth')
        },
        'weather': {
            'humidity': ('>70', 'High humidity favorable for fungal development'),
            'temperature': ('range:15-30', 'Optimal temperature range for fungal growth')
        }
    },
    'BACTERIAL': {
        'soil': {
            'moisture': ('>60', 'Waterlogged conditions favorable for bacterial pathogens'),
            'temperature': ('>25', 'Warm soil temperatures accelerate bacterial growth')
        },
        'weather': {
            'temperature': ('>25', 'Warm temperatures accelerate bacterial reproduction'),
            'humidity': ('>65', 'Moist conditions favor bacterial spread')
        }
    },
    'VIRAL': {
        'weather': {
            'temperature': ('range:15-25', 'Optimal for insect vector activity'),
            'wind_speed': ('>5', 'Sufficient for viral particle spread')
        }
    },
    'PEST': {
        'soil': {
            'moisture': ('<30', 'Dry conditions favor certain pest infestations'),
            'temperature': ('>20', 'Warm soil accelerates pest development')
        },
        'weather': {
            'temperature': ('>20', 'Warm conditions increase pest reproduction rates'),
            'humidity': ('<50', 'Low humidity favors certain insect pests')
        }
    }
}

# Thresholds for threat levels
THREAT_LEVEL_THRESHOLDS = {
    'confidence': {
        'CRITICAL': 0.9,
        'HIGH': 0.75,
        'MEDIUM': 0.6,
        'LOW': 0.4
    },
    'deviation': {
        'CRITICAL': 2.5,
        'HIGH': 2.0, 
        'MEDIUM': 1.5,
        'LOW': 1.0
    }
}

def detect_anomalies(features: Dict[str, float], sensor_type: str) -> Tuple[List[str], float]:
    """
    Detect anomalies in sensor data using both rule-based and model-based approaches.
    
    Args:
        features: Dictionary of feature values
        sensor_type: Type of sensor (soil, weather, etc.)
        
    Returns:
        Tuple containing list of anomalies detected and confidence level
    """
    # Initialize results
    anomalies = []
    confidence = 0.0
    
    # First do rule-based detection (faster and more interpretable)
    rule_anomalies, rule_confidence = rule_based_detection(features, sensor_type)
    anomalies.extend(rule_anomalies)
    
    # If no rule-based anomalies found, use model-based detection
    if not anomalies:
        model_anomalies, model_confidence = model_based_detection(features, sensor_type)
        anomalies.extend(model_anomalies)
        confidence = model_confidence
    else:
        confidence = rule_confidence
    
    return anomalies, confidence

def rule_based_detection(features: Dict[str, float], sensor_type: str) -> Tuple[List[str], float]:
    """
    Detect anomalies using predefined rules and normal ranges.
    
    Args:
        features: Dictionary of feature values
        sensor_type: Type of sensor
        
    Returns:
        Tuple of anomalies and confidence
    """
    anomalies = []
    confidence_scores = []
    
    # Check if values are outside normal ranges
    normal_ranges = NORMAL_RANGES.get(sensor_type, {})
    for feature, value in features.items():
        if feature in normal_ranges:
            min_val, max_val = normal_ranges[feature]
            
            # Calculate how far outside the range it is (if at all)
            if value < min_val:
                deviation = (min_val - value) / (min_val * 0.1)  # Normalize by 10% of min value
                anomalies.append(f"Low {feature}: {value} (normal range: {min_val}-{max_val})")
                confidence_scores.append(min(0.95, 0.5 + (deviation * 0.1)))
            elif value > max_val:
                deviation = (value - max_val) / (max_val * 0.1)  # Normalize by 10% of max value
                anomalies.append(f"High {feature}: {value} (normal range: {min_val}-{max_val})")
                confidence_scores.append(min(0.95, 0.5 + (deviation * 0.1)))
    
    # If at least one anomaly, return the average confidence
    if anomalies:
        return anomalies, sum(confidence_scores) / len(confidence_scores)
    
    # No anomalies found with rule-based detection
    return [], 0.0

def model_based_detection(features: Dict[str, float], sensor_type: str) -> Tuple[List[str], float]:
    """
    Detect anomalies using machine learning model (Isolation Forest).
    
    Args:
        features: Dictionary of feature values
        sensor_type: Type of sensor
        
    Returns:
        Tuple of anomalies and confidence
    """
    try:
        # Convert features to numpy array in the correct order
        feature_names = list(features.keys())
        feature_values = np.array([features[name] for name in feature_names]).reshape(1, -1)
        
        # Load model if it exists, otherwise create a new one
        model_path = f"models/{sensor_type}_anomaly_model.joblib"
        model = None
        
        # If model exists, load it
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            logger.info(f"Loaded existing anomaly detection model for {sensor_type}")
        else:
            # In real application, we'd train on historical data
            # For now, initialize a new model with default parameters
            model = IsolationForest(
                contamination=0.05,  # Assume 5% of data are anomalies
                random_state=42,
                n_estimators=100
            )
            logger.info(f"Created new anomaly detection model for {sensor_type} (would normally train on historical data)")
        
        # Normalize the features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_values)
        
        # Predict anomaly score (-1 for anomalies, 1 for normal)
        # and get anomaly score (negative of prediction, higher = more anomalous)
        prediction = model.predict(scaled_features)[0]
        anomaly_score = model.decision_function(scaled_features)[0]
        
        # Convert to confidence (0-1 scale, where 1 = certain anomaly)
        confidence = 1.0 - (1.0 + anomaly_score) / 2.0 if anomaly_score < 0 else 0.0
        
        # If prediction is anomaly
        if prediction == -1 and confidence > 0.6:
            # Determine which features are most anomalous
            # In a real implementation, this would be more sophisticated
            anomalies = [f"Unusual {sensor_type} sensor pattern detected"]
            return anomalies, confidence
        
        # No anomalies detected by model
        return [], 0.0
        
    except Exception as e:
        logger.error(f"Error in model-based anomaly detection: {str(e)}")
        return [], 0.0

def evaluate_threat_level(anomalies: List[str], confidence: float, sensor_type: str) -> Tuple[str, str]:
    """
    Evaluate the type and level of threat based on detected anomalies.
    
    Args:
        anomalies: List of anomaly descriptions
        confidence: Confidence level of anomaly detection
        sensor_type: Type of sensor that produced the data
        
    Returns:
        Tuple of (threat_type, threat_level)
    """
    # Default values
    threat_type = "UNKNOWN"
    threat_level = "LOW"
    
    # If there are no anomalies, return defaults
    if not anomalies:
        return threat_type, threat_level
    
    # Join anomalies into a single string for pattern matching
    anomaly_text = " ".join(anomalies).lower()
    
    # Check for specific patterns indicating different threats
    # This is a simplified version - a real implementation would be more sophisticated
    
    # Detect potential threat types
    threat_scores = {
        "FUNGAL": 0.0,
        "BACTERIAL": 0.0,
        "VIRAL": 0.0,
        "PEST": 0.0,
        "BIOWEAPON": 0.0,
        "UNKNOWN": 0.1  # Small bias towards unknown
    }
    
    # Look for keywords suggesting specific threats
    if sensor_type == 'soil':
        # Fungal indicators
        if 'high moisture' in anomaly_text or 'moisture: high' in anomaly_text:
            threat_scores["FUNGAL"] += 0.3
        if 'low ph' in anomaly_text or 'acidic' in anomaly_text:
            threat_scores["FUNGAL"] += 0.2
        
        # Bacterial indicators
        if 'high temperature' in anomaly_text and 'high moisture' in anomaly_text:
            threat_scores["BACTERIAL"] += 0.4
        
        # Pest indicators
        if 'low moisture' in anomaly_text or 'dry' in anomaly_text:
            threat_scores["PEST"] += 0.2
        if 'high temperature' in anomaly_text:
            threat_scores["PEST"] += 0.2
    
    elif sensor_type == 'weather':
        # Fungal indicators
        if 'high humidity' in anomaly_text:
            threat_scores["FUNGAL"] += 0.3
        if 'precipitation' in anomaly_text and 'high' in anomaly_text:
            threat_scores["FUNGAL"] += 0.25
            
        # Viral indicators (often spread by wind)
        if 'wind' in anomaly_text and 'high' in anomaly_text:
            threat_scores["VIRAL"] += 0.3
            
        # Pest indicators
        if 'high temperature' in anomaly_text:
            threat_scores["PEST"] += 0.2
    
    # Adjust scores based on confidence
    for threat in threat_scores:
        threat_scores[threat] *= confidence
    
    # Find the most likely threat type
    most_likely_threat = max(threat_scores.items(), key=lambda x: x[1])
    
    # Only assign a specific threat if it's reasonably likely
    if most_likely_threat[1] > 0.2:
        threat_type = most_likely_threat[0]
    else:
        threat_type = "UNKNOWN"
    
    # Determine threat level based on confidence and anomaly severity
    if confidence >= THREAT_LEVEL_THRESHOLDS['confidence']['CRITICAL']:
        threat_level = "CRITICAL"
    elif confidence >= THREAT_LEVEL_THRESHOLDS['confidence']['HIGH']:
        threat_level = "HIGH"
    elif confidence >= THREAT_LEVEL_THRESHOLDS['confidence']['MEDIUM']:
        threat_level = "MEDIUM"
    elif confidence >= THREAT_LEVEL_THRESHOLDS['confidence']['LOW']:
        threat_level = "LOW"
    else:
        threat_level = "LOW"
    
    logger.info(f"Evaluated threat as {threat_type} with {threat_level} severity ({confidence:.2f} confidence)")
    return threat_type, threat_level


def train_anomaly_detection_model(historical_data: List[Dict[str, float]], sensor_type: str) -> None:
    """
    Train an anomaly detection model using historical data.
    
    Args:
        historical_data: List of sensor readings (each a dictionary of features)
        sensor_type: Type of sensor the data came from
    """
    try:
        logger.info(f"Training anomaly detection model for {sensor_type} sensor")
        
        # Extract features from historical data
        feature_names = list(historical_data[0].keys())
        X = np.array([[reading[feature] for feature in feature_names] for reading in historical_data])
        
        # Normalize the data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train the Isolation Forest model
        model = IsolationForest(
            contamination=0.05,  # Assume 5% of historical data are anomalies
            random_state=42,
            n_estimators=100
        )
        model.fit(X_scaled)
        
        # Save the model
        os.makedirs("models", exist_ok=True)
        model_path = f"models/{sensor_type}_anomaly_model.joblib"
        joblib.dump(model, model_path)
        
        # Also save the scaler
        scaler_path = f"models/{sensor_type}_scaler.joblib"
        joblib.dump(scaler, scaler_path)
        
        logger.info(f"Successfully trained and saved anomaly detection model for {sensor_type}")
        
    except Exception as e:
        logger.error(f"Error training anomaly detection model: {str(e)}")

