import logging
import numpy as np
import requests
import cv2
import os
import tempfile
import io
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from PIL import Image
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Dictionary of known crop disease patterns
# In a real application, this would be replaced with a trained classification model
DISEASE_PATTERNS = {
    'fungal_leaf_spot': {
        'description': 'Fungal leaf spot disease characterized by brown/black spots on leaves',
        'color_range': [(30, 20, 20), (80, 60, 60)],  # BGR color range for detection
        'min_area_ratio': 0.01,  # Minimum area as ratio of total image
        'threat_type': 'FUNGAL',
        'recommendations': [
            "Collect and destroy affected leaves",
            "Apply appropriate fungicide treatment",
            "Increase air circulation around plants"
        ]
    },
    'powdery_mildew': {
        'description': 'Powdery mildew infection showing white powdery growth on leaves',
        'color_range': [(200, 200, 200), (255, 255, 255)],
        'min_area_ratio': 0.03,
        'threat_type': 'FUNGAL',
        'recommendations': [
            "Apply sulfur-based fungicide",
            "Reduce humidity around plants",
            "Remove and destroy severely affected plant parts"
        ]
    },
    'bacterial_blight': {
        'description': 'Bacterial blight showing water-soaked lesions turning yellow to brown',
        'color_range': [(0, 100, 100), (30, 180, 180)],
        'min_area_ratio': 0.02,
        'threat_type': 'BACTERIAL',
        'recommendations': [
            "Remove infected plants immediately",
            "Disinfect tools and equipment",
            "Apply copper-based bactericide to protect surrounding plants"
        ]
    },
    'viral_mosaic': {
        'description': 'Viral mosaic disease showing mottled green/yellow pattern on leaves',
        'color_range': [(20, 180, 20), (60, 255, 60)],
        'min_area_ratio': 0.05,
        'threat_type': 'VIRAL',
        'recommendations': [
            "Remove and destroy infected plants",
            "Control insect vectors with appropriate insecticides",
            "Ensure proper sanitation of tools and equipment"
        ]
    },
    'insect_damage': {
        'description': 'Physical damage from insect pests visible on leaves/stems',
        'color_range': [(0, 0, 0), (50, 50, 50)],
        'min_area_ratio': 0.01,
        'threat_type': 'PEST',
        'recommendations': [
            "Apply appropriate insecticide or biological controls",
            "Install insect traps around field perimeter",
            "Introduce beneficial predator insects if appropriate"
        ]
    }
}


def download_image(url: str) -> Optional[np.ndarray]:
    """
    Download an image from a URL and convert it to OpenCV format.
    
    Args:
        url: URL of the image to download
        
    Returns:
        Image as numpy array (OpenCV format) or None if failed
    """
    try:
        logger.info(f"Downloading image from: {url}")
        
        # Handle different URL formats
        if url.startswith('data:image'):
            # Handle data URLs (base64 encoded images)
            encoded_data = url.split(',')[1]
            img_data = base64.b64decode(encoded_data)
            image = Image.open(io.BytesIO(img_data))
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            # Handle regular URLs
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Save to a temporary file and read with OpenCV
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Read image with OpenCV
            img = cv2.imread(temp_file_path)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return img
            
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        return None


def detect_disease_pattern(image: np.ndarray, pattern_name: str, pattern_info: Dict[str, Any]) -> Tuple[bool, float, Dict[str, Any]]:
    """
    Detect a specific disease pattern in an image.
    
    Args:
        image: Image in OpenCV format (numpy array)
        pattern_name: Name of the pattern to detect
        pattern_info: Dictionary with pattern detection parameters
        
    Returns:
        Tuple of (detected, confidence, affected_area_info)
    """
    try:
        # Make a copy of the image
        img_copy = image.copy()
        
        # Create a mask for the specified color range
        lower_bound = np.array(pattern_info['color_range'][0])
        upper_bound = np.array(pattern_info['color_range'][1])
        mask = cv2.inRange(img_copy, lower_bound, upper_bound)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate total image area
        total_area = img_copy.shape[0] * img_copy.shape[1]
        
        # Calculate area covered by the disease pattern
        disease_area = 0
        affected_contours = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > total_area * pattern_info['min_area_ratio']:
                disease_area += area
                affected_contours.append(contour)
        
        # Calculate ratio of affected area
        affected_ratio = disease_area / total_area
        
        # Calculate a confidence level based on the affected ratio
        # Higher ratio = higher confidence
        confidence = min(0.95, affected_ratio * 10)
        
        # Determine if pattern is detected based on area threshold
        detected = affected_ratio > pattern_info['min_area_ratio']
        
        # If detected, calculate bounding boxes and center points of affected areas
        affected_areas = []
        if detected:
            for contour in affected_contours:
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                affected_areas.append({
                    'position': (center_x, center_y),
                    'area': cv2.contourArea(contour),
                    'bounding_box': (x, y, w, h)
                })
        
        return detected, confidence, {
            'affected_ratio': affected_ratio,
            'affected_areas': affected_areas
        }
        
    except Exception as e:
        logger.error(f"Error detecting {pattern_name} pattern: {str(e)}")
        return False, 0.0, {}


def analyze_crop_image(image_url: str, image_type: str = 'RGB') -> Optional[Dict[str, Any]]:
    """
    Analyze a crop image to detect signs of disease.
    
    Args:
        image_url: URL or path to the image
        image_type: Type of image (RGB, infrared, etc.)
        
    Returns:
        Dictionary with analysis results or None if analysis failed
    """
    try:
        logger.info(f"Analyzing crop image of type {image_type}")
        
        # Download the image
        img = download_image(image_url)
        if img is None:
            logger.error("Failed to download or read image")
            return None
        
        # Store image dimensions
        height, width = img.shape[:2]
        
        # Preprocess based on image type
        if image_type == 'RGB':
            # For RGB images, use as-is
            processed_img = img
        elif image_type == 'IR' or image_type == 'infrared':
            # For infrared images, apply specific pre-processing
            # Convert to grayscale and enhance contrast
            processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            processed_img = cv2.equalizeHist(processed_img)
            processed_img = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2BGR)
        else:
            # Default processing for other image types
            processed_img = img
        
        # Detect disease patterns
        results = []
        for pattern_name, pattern_info in DISEASE_PATTERNS.items():
            detected, confidence, area_info = detect_disease_pattern(
                processed_img, pattern_name, pattern_info
            )
            
            if detected:
                results.append({
                    'pattern': pattern_name,
                    'confidence': confidence,
                    'description': pattern_info['description'],
                    'threat_type': pattern_info['threat_type'],
                    'area_info': area_info,
                    'recommendations': pattern_info['recommendations']
                })
        
        # If no diseases detected, return None
        if not results:
            logger.info("No disease patterns detected in image")
            return None
        
        # Sort results by confidence and get the most confident detection
        results.sort(key=lambda x: x['confidence'], reverse=True)
        top_result = results[0]
        
        # Determine severity based on affected area and confidence
        severity = "LOW"
        affected_ratio = top_result['area_info']['affected_ratio']
        if affected_ratio > 0.25 and top_result['confidence'] > 0.8:
            severity = "CRITICAL"
        elif affected_ratio > 0.15 and top_result['confidence'] > 0.7:
            severity = "HIGH"
        elif affected_ratio > 0.05 and top_result['confidence'] > 0.6:
            severity = "MEDIUM"
        
        return {
            'disease_type': top_result['threat_type'],
            'confidence': top_result['confidence'],
            'description': f"{top_result['pattern']} detected: {top_result['description']}",
            'severity': severity,
            'affected_ratio': affected_ratio,
            'image_dimensions': (width, height),
            'recommendations': top_result['recommendations'],
            'all_detections': results
        }
        
    except Exception as e:
        logger.error(f"Error analyzing crop image: {str(e)}")
        return None


def process_image_batch(image_urls: List[str], image_type: str = 'RGB') -> List[Dict[str, Any]]:
    """
    Process a batch of images for disease detection.
    
    Args:
        image_urls: List of URLs to process
        image_type: Type of images
        
    Returns:
        List of detection results
    """
    results = []
    
    for url in image_urls:
        result = analyze_crop_image(url, image_type)
        if result:
            results.append({
                'url': url,
                'analysis': result
            })
    
    return results

