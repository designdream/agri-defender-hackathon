import os
import logging
import psycopg2
from psycopg2.extras import Json, DictCursor
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Database connection parameters
DB_PARAMS = {
    "dbname": os.getenv("POSTGRES_DB", "agridefender"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

# Redis connection parameters
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

def get_db():
    """
    Create and return a database connection.
    This function is used as a dependency in FastAPI endpoints.
    """
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()
            logger.debug("Database connection closed")

def get_redis():
    """
    Create and return a Redis connection.
    This function is used as a dependency in FastAPI endpoints.
    """
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        yield r
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        raise
    finally:
        if 'r' in locals() and r is not None:
            r.close()
            logger.debug("Redis connection closed")

def check_db_connection():
    """
    Check if the database connection is working.
    Returns True if connection is successful, False otherwise.
    If MOCK_MODE is enabled, always returns True.
    """
    if os.getenv("MOCK_MODE", "False").lower() == "true":
        logger.info("Mock mode enabled: Simulating successful database connection")
        return True
        
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False

def check_redis_connection():
    """
    Check if the Redis connection is working.
    Returns True if connection is successful, False otherwise.
    If MOCK_MODE is enabled, always returns True.
    """
    if os.getenv("MOCK_MODE", "False").lower() == "true":
        logger.info("Mock mode enabled: Simulating successful Redis connection")
        return True
        
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        r.ping()
        r.close()
        return True
    except Exception as e:
        logger.error(f"Redis connection check failed: {str(e)}")
        return False

def init_db():
    """
    Initialize the database with required tables if they don't exist.
    This function should be called when the application starts.
    """
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id VARCHAR(36) PRIMARY KEY,
            sensor_type VARCHAR(50) NOT NULL,
            location JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_reading_at TIMESTAMP WITH TIME ZONE,
            metadata JSONB
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id VARCHAR(36) PRIMARY KEY,
            sensor_id VARCHAR(36) REFERENCES sensors(id),
            reading_time TIMESTAMP WITH TIME ZONE NOT NULL,
            data JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS threats (
            id VARCHAR(36) PRIMARY KEY,
            threat_type VARCHAR(50) NOT NULL,
            threat_level VARCHAR(20) NOT NULL,
            confidence FLOAT NOT NULL,
            detection_time TIMESTAMP WITH TIME ZONE NOT NULL,
            location JSONB NOT NULL,
            description TEXT,
            recommendations JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id VARCHAR(36) PRIMARY KEY,
            threat_id VARCHAR(36) REFERENCES threats(id),
            prediction_time TIMESTAMP WITH TIME ZONE NOT NULL,
            threat_level VARCHAR(20) NOT NULL,
            confidence FLOAT NOT NULL,
            location JSONB NOT NULL,
            affected_area JSONB,
            probability FLOAT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        if 'conn' in locals() and conn is not None:
            conn.rollback()
            conn.close()
        return False
