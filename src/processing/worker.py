import logging
import time
import os
import json
import redis
import signal
import sys
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import uuid
import psycopg2
from psycopg2.extras import Json

from src.processing.anomaly_detection import detect_anomalies, evaluate_threat_level
from src.processing.image_processing import analyze_crop_image
from src.processing.geospatial import map_threat_area, predict_spread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True

class ProcessingWorker:
    """
    Main worker class that processes incoming sensor data and detects biological threats.
    """
    
    def __init__(self):
        """Initialize the processing worker with connections to Redis and PostgreSQL"""
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0
        )
        
        # Database connection will be established in connect_to_db method
        self.db_conn = None
        self.connect_to_db()
        
        # Processing queues
        self.soil_queue = "sensor:soil:queue"
        self.weather_queue = "sensor:weather:queue"
        self.image_queue = "sensor:image:queue"
        
        # Tracking processed items
        self.processed_count = 0
        self.last_processed_time = datetime.now()
        
        logger.info("Processing worker initialized")
    
    def connect_to_db(self) -> None:
        """Establish connection to PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                database=os.getenv('POSTGRES_DB', 'agridefender'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres')
            )
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            # In a production environment, you might want to implement retry logic
            raise
    
    def process_soil_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process soil sensor data to detect anomalies"""
        try:
            logger.info(f"Processing soil data from sensor {data.get('sensor_id')}")
            
            # Extract relevant features for anomaly detection
            features = {
                'moisture': data.get('moisture', 0),
                'ph': data.get('ph', 0),
                'temperature': data.get('temperature', 0),
                'nitrogen': data.get('nitrogen', 0),
                'phosphorus': data.get('phosphorus', 0),
                'potassium': data.get('potassium', 0)
            }
            
            # Detect anomalies in soil data
            anomalies, confidence = detect_anomalies(features, sensor_type='soil')
            
            if not anomalies:
                logger.info("No anomalies detected in soil data")
                return None
            
            # If anomalies detected, evaluate threat level and create detection
            threat_type, threat_level = evaluate_threat_level(anomalies, confidence, 'soil')
            
            # Map the potential affected area
            location = data.get('location', {})
            affected_area = map_threat_area(
                location, 
                threat_type, 
                data.get('sensor_id'), 
                radius_meters=500
            )
            
            # Create threat detection object
            detection = {
                'id': str(uuid.uuid4()),
                'threat_type': threat_type,
                'threat_level': threat_level,
                'detection_time': datetime.now().isoformat(),
                'confidence': confidence,
                'location': location,
                'affected_area': affected_area,
                'description': f"Abnormal soil conditions detected: {', '.join(anomalies)}",
                'recommendations': self._generate_recommendations(threat_type, threat_level),
                'source_data': [data.get('sensor_id')]
            }
            
            logger.info(f"Detected {threat_type} threat with {threat_level} severity")
            return detection
            
        except Exception as e:
            logger.error(f"Error processing soil data: {str(e)}")
            return None
    
    def process_weather_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process weather sensor data to detect conditions favorable for pathogens"""
        try:
            logger.info(f"Processing weather data from sensor {data.get('sensor_id')}")
            
            # Extract relevant features
            features = {
                'temperature': data.get('temperature', 0),
                'humidity': data.get('humidity', 0),
                'precipitation': data.get('precipitation', 0),
                'wind_speed': data.get('wind_speed', 0),
                'wind_direction': data.get('wind_direction', 0),
            }
            
            # Detect weather conditions that may facilitate pathogen spread
            anomalies, confidence = detect_anomalies(features, sensor_type='weather')
            
            if not anomalies:
                logger.info("No concerning weather patterns detected")
                return None
            
            # Evaluate threat based on weather conditions
            threat_type, threat_level = evaluate_threat_level(anomalies, confidence, 'weather')
            
            # Map area potentially affected by weather conditions
            location = data.get('location', {})
            affected_area = map_threat_area(
                location, 
                threat_type, 
                data.get('sensor_id'),
                radius_meters=2000  # Weather affects larger areas
            )
            
            # Create threat detection object
            detection = {
                'id': str(uuid.uuid4()),
                'threat_type': threat_type,
                'threat_level': threat_level,
                'detection_time': datetime.now().isoformat(),
                'confidence': confidence,
                'location': location,
                'affected_area': affected_area,
                'description': f"Weather conditions favorable for {threat_type} development detected",
                'recommendations': self._generate_recommendations(threat_type, threat_level),
                'source_data': [data.get('sensor_id')]
            }
            
            logger.info(f"Detected weather conditions favorable for {threat_type}")
            return detection
            
        except Exception as e:
            logger.error(f"Error processing weather data: {str(e)}")
            return None
    
    def process_image_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process image data to detect visual signs of crop diseases"""
        try:
            logger.info(f"Processing image data from sensor {data.get('sensor_id')}")
            
            # Get image URL and analyze it
            image_url = data.get('image_url')
            if not image_url:
                logger.warning("Image URL missing in image data")
                return None
            
            # Analyze the image for disease patterns
            disease_results = analyze_crop_image(
                image_url,
                image_type=data.get('image_type', 'RGB')
            )
            
            if not disease_results or disease_results.get('confidence', 0) < 0.6:
                logger.info("No diseases detected in the image or confidence too low")
                return None
            
            # Create threat detection from image analysis
            location = data.get('location', {})
            affected_area = data.get('coverage_area')  # The image itself shows the affected area
            
            # Create threat detection object
            detection = {
                'id': str(uuid.uuid4()),
                'threat_type': disease_results.get('disease_type', 'UNKNOWN'),
                'threat_level': disease_results.get('severity', 'MEDIUM'),
                'detection_time': datetime.now().isoformat(),
                'confidence': disease_results.get('confidence', 0.7),
                'location': location,
                'affected_area': affected_area,
                'description': disease_results.get('description', 'Potential crop disease detected in image'),
                'recommendations': disease_results.get('recommendations', []),
                'source_data': [data.get('sensor_id'), image_url]
            }
            
            logger.info(f"Detected {detection['threat_type']} in image with {detection['confidence']:.2f} confidence")
            return detection
            
        except Exception as e:
            logger.error(f"Error processing image data: {str(e)}")
            return None
    
    def _generate_recommendations(self, threat_type: str, threat_level: str) -> List[str]:
        """Generate action recommendations based on the threat type and level"""
        recommendations = []
        
        if threat_type == 'FUNGAL':
            recommendations.append("Inspect affected areas for signs of fungal growth")
            if threat_level in ['HIGH', 'CRITICAL']:
                recommendations.append("Apply approved fungicide treatment immediately")
                recommendations.append("Consider crop isolation measures")
            else:
                recommendations.append("Monitor closely for 48 hours")
                recommendations.append("Prepare fungicide application equipment")
        
        elif threat_type == 'BACTERIAL':
            recommendations.append("Test plant tissue samples to confirm bacterial infection")
            if threat_level in ['HIGH', 'CRITICAL']:
                recommendations.append("Remove and destroy infected plants")
                recommendations.append("Apply copper-based bactericide to surrounding areas")
            else:
                recommendations.append("Reduce overhead irrigation to minimize spread")
        
        elif threat_type == 'VIRAL':
            recommendations.append("Identify and control insect vectors in the area")
            recommendations.append("Remove infected plants if virus is confirmed")
            if threat_level in ['HIGH', 'CRITICAL']:
                recommendations.append("Establish buffer zones around affected areas")
                recommendations.append("Implement strict decontamination for field workers and equipment")
        
        elif threat_type == 'PEST':
            recommendations.append("Deploy traps to monitor pest population")
            if threat_level in ['HIGH', 'CRITICAL']:
                recommendations.append("Apply appropriate pesticide treatment")
                recommendations.append("Consider biological control methods")
            else:
                recommendations.append("Increase monitoring frequency")
        
        elif threat_type == 'BIOWEAPON':
            recommendations.append("Immediately restrict access to affected area")
            recommendations.append("Contact agricultural security authorities")
            recommendations.append("Document all observations and secure evidence")
            recommendations.append("Do NOT attempt remediation without expert guidance")
        
        # Add general recommendations
        recommendations.append("Document all observations with photos and notes")
        recommendations.append("Update AgriDefender system with field observations")
        
        return recommendations
    
    def save_detection(self, detection: Dict[str, Any]) -> bool:
        """Save a threat detection to the database"""
        try:
            cursor = self.db_conn.cursor()
            
            # Insert into detections table
            query = """
            INSERT INTO detections (
                id, threat_type, threat_level, detection_time, confidence, 
                location, affected_area, description, recommendations, source_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(
                query,
                (
                    detection['id'],
                    detection['threat_type'],
                    detection['threat_level'],
                    detection['detection_time'],
                    detection['confidence'],
                    Json(detection['location']),
                    Json(detection['affected_area']) if detection['affected_area'] else None,
                    detection['description'],
                    Json(detection['recommendations']),
                    Json(detection['source_data'])
                )
            )
            
            self.db_conn.commit()
            cursor.close()
            
            # Also publish to Redis for real-time notifications
            self.redis_client.publish(
                'threat:detections', 
                json.dumps(detection)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving detection to database: {str(e)}")
            if self.db_conn:
                self.db_conn.rollback()
            return False
    
    def generate_predictions(self, detection: Dict[str, Any]) -> None:
        """Generate and store predictions for threat spread"""
        try:
            # Only generate predictions for medium or higher threats
            if detection['threat_level'] in ['LOW']:
                return
            
            # Generate spread predictions
            predictions = predict_spread(
                threat_id=detection['id'],
                threat_type=detection['threat_type'],
                location=detection['location'],
                detection_time=detection['detection_time'],
                current_weather=self._get_current_weather(detection['location'])
            )
            
            if not predictions:
                logger.info(f"No spread predictions generated for threat {detection['id']}")
                return
            
            # Save predictions to database
            cursor = self.db_conn.cursor()
            
            for prediction in predictions:
                query = """
                INSERT INTO predictions (
                    id, threat_id, prediction_time, threat_level, confidence,
                    location, affected_area, probability
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(
                    query,
                    (
                        str(uuid.uuid4()),
                        detection['id'],
                        prediction['prediction_time'],
                        prediction['threat_level'],
                        prediction['confidence'],
                        Json(prediction['location']),
                        Json(prediction['affected_area']) if prediction.get('affected_area') else None,
                        prediction['probability']
                    )
                )
            
            self.db_conn.commit()
            cursor.close()
            
            logger.info(f"Saved {len(predictions)} spread predictions for threat {detection['id']}")
            
        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            if self.db_conn:
                self.db_conn.rollback()
    
    def _get_current_weather(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get current weather data for a location (mock implementation)"""
        # In a real implementation, this would query a weather service or database
        return {
            'temperature': 25.5,
            'humidity': 65.0,
            'wind_speed': 10.2,
            'wind_direction': 180,
            'precipitation': 0.0
        }
    
    def process_sensor_data(self, sensor_type: str, data: Dict[str, Any]) -> None:
        """Process sensor data based on its type"""
        detection = None
        
        if sensor_type == 'soil':
            detection = self.process_soil_data(data)
        elif sensor_type == 'weather':
            detection = self.process_weather_data(data)
        elif sensor_type == 'image':
            detection = self.process_image_data(data)
        
        # If a threat was detected, save it and generate predictions
        if detection:
            if self.save_detection(detection):
                self.generate_predictions(detection)
                self.processed_count += 1
    
    def run(self) -> None:
        """Main processing loop that pulls data from queues and processes it"""
        logger.info("Starting processing worker loop")
        
        while running:
            try:
                # Check soil data queue
                soil_data = self.redis_client.lpop(self.soil_queue)
                if soil_data:
                    self.process_sensor_data('soil', json.loads(soil_data))
                
                # Check weather data queue
                weather_data = self.redis_client.lpop(self.weather_queue)
                if weather_data:
                    self.process_sensor_data('weather', json.loads(weather_data))
                
                # Check image data queue
                image_data = self.redis_client.lpop(self.image_queue)
                if image_data:
                    self.process_sensor_data('image', json.loads(image_data))
                
                # If no data was processed, sleep briefly
                if not soil_data and not weather_data and not image_data:
                    time.sleep(0.1)
                    
                # Periodically log processing statistics
                now = datetime.now()
                if (now - self.last_processed_time).total_seconds() > 60:
                    logger.info(f"Processed {self.processed_count} items in the last minute")
                    self.processed_count = 0
                    self.last_processed_time = now
                    
            except Exception as e:
                logger.error(f"Error in processing loop: {str(e)}")
                # Sleep briefly to avoid tight error loop
                time.sleep(1)
    
    def stop(self) -> None:
        """Stop the processing worker"""
        logger.info("Stopping processing worker")
        if self.db_conn:
            self.db_conn.close()


def signal_handler(sig, frame):
    """Handle termination signals to stop gracefully"""
    global running
    logging.info(f"Received signal {sig}, shutting down...")
    running = False


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run the worker
    worker = ProcessingWorker()
    
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
    finally:
        worker.stop()
        sys.exit(0)

