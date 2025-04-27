# AgriDefender - Agricultural Biological Threat Detection System

AgriDefender is a comprehensive system for detecting, monitoring, predicting, and responding to biological threats to agriculture. This application integrates cutting-edge research concepts from agricultural defense studies to provide farmers and agricultural authorities with powerful tools for protecting crops.

## Project Overview

AgriDefender combines multiple defense strategies into a unified platform:

1. **Early Detection** - Sensors, image analysis, and community reporting to identify threats at their earliest stages
2. **Predictive Modeling** - LSTM-based neural networks to forecast how pathogens might spread
3. **Response Coordination** - Containment protocols and community alerts to minimize impact
4. **Natural Defense** - Companion planting strategies to build resilience against threats

## Architecture

The application is structured as follows:

```
├── src/
│   ├── api/                 # FastAPI backend
│   │   ├── routes/          # API endpoints for different features
│   │   └── models.py        # Data models
│   ├── dashboard/           # Streamlit frontend
│   │   ├── components/      # UI components for different features  
│   │   └── app.py           # Main dashboard application
│   ├── models/              # ML models for prediction and analysis
│   └── processing/          # Data processing pipelines
├── tests/                   # Test cases
├── research/                # Research materials and references
└── docs/                    # Documentation
```

## Research Implementation

AgriDefender incorporates several key research concepts from the agricultural defense hackathon:

### 1. AI Diagnostic Assistant (Image Analysis)

**Research Concept:** A mobile application using machine learning to identify plant diseases from smartphone photos, providing immediate diagnostic information and treatment recommendations.

**Implementation:**
- API endpoint: `/api/v1/threats/image-analysis`
- Frontend: `dashboard/components/image_analysis.py`
- Features:
  - Image upload and analysis
  - Threat identification with confidence scores
  - Treatment recommendations
  - Integration with containment planning and community alerts

### 2. Blockchain Biosecurity Ledger

**Research Concept:** A transparent, immutable record-keeping system using blockchain technology to track agricultural inputs, disease occurrences, and treatments.

**Implementation:**
- API endpoint: `/api/v1/threats/verify-report`
- Integration: Embedded within the image analysis and threat reporting workflows
- Features:
  - Verification of threat reports
  - Immutable record of detection and response actions
  - Transaction tracking for auditing and traceability

### 3. Crowdsourced Disease Mapping & Community Alert System

**Research Concept:** A collaborative platform allowing farmers to report disease occurrences and alert nearby farmers about emerging threats.

**Implementation:**
- API endpoint: `/api/v1/threats/community-alert`
- Frontend: Integrated within image analysis component
- Features:
  - Geofenced alert distribution
  - Multi-channel notifications (SMS, email, app)
  - Estimated recipient calculation

### 4. Rapid Containment Protocol

**Research Concept:** An automated system that implements immediate quarantine and treatment measures upon disease detection.

**Implementation:**
- API endpoint: `/api/v1/threats/{threat_id}/containment-plan`
- Frontend: Containment plan display within image analysis workflow
- Features:
  - Prioritized immediate actions
  - Follow-up action schedules
  - Equipment requirements
  - Step-by-step containment guidance

### 5. Companion Planting Optimizer

**Research Concept:** An AI-driven planning tool that designs optimal combinations of plants to naturally suppress pests and diseases.

**Implementation:**
- API endpoint: `/api/v1/threats/companion-plants`
- Frontend: `dashboard/components/companion_planting.py`
- Features:
  - Crop and threat-specific recommendations
  - Compatibility scoring
  - Visual planting pattern diagram
  - Seasonal timing information
  - Downloadable implementation plans

## Key Features

### Threat Detection and Monitoring
- Real-time data collection from various sensor types
- Image-based disease identification
- Manual and automated threat reporting
- Geospatial visualization of threats

### Predictive Analytics
- Pathogen spread prediction using LSTM neural networks
- Time-series forecasting
- GeoJSON visualization of predicted affected areas
- Confidence scoring for predictions

### Response Coordination
- Automated containment protocols
- Community alerting system
- Treatment recommendations
- Equipment and resource planning

### Natural Defense Strategies
- Companion planting recommendations
- Planting pattern visualization
- Seasonal timing guidance
- Protection level estimation

## Getting Started

### Prerequisites
- Python 3.8+
- Docker and Docker Compose (for containerized deployment)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/defense-hackathon.git
cd defense-hackathon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the application using Docker Compose:
```bash
docker-compose up
```

4. Access the dashboard at http://localhost:8501 and the API at http://localhost:8000

### Development Setup

1. Start the API server:
```bash
cd src
python -m api.main
```

2. In a separate terminal, start the Streamlit dashboard:
```bash
cd src
streamlit run dashboard/app.py
```

## Next Steps and Future Enhancements

### Live API Integration
- Replace mock data with actual API calls
- Implement proper error handling for API failures
- Add caching for performance optimization

### ML Model Development
- Train computer vision models on plant disease datasets
- Implement actual blockchain verification
- Create real companion planting optimization algorithms

## Machine Learning Implementation Guide

To fully realize the potential of the research concepts, several ML models need to be developed:

### 1. Plant Disease Identification Model

**Purpose:** Enable the AI Diagnostic Assistant to accurately identify plant diseases from images

**Suggested Approach:**
- **Architecture:** Convolutional Neural Network (CNN) such as ResNet50 or EfficientNet
- **Training Data:** Large dataset of labeled plant disease images (50,000+ images)
- **Features:** 
  - Multi-class classification for different disease types
  - Confidence scoring
  - Bounding box detection for affected areas
  - Transfer learning from pre-trained models for efficiency

**Implementation Path:**
1. Collect and label crop disease images
2. Fine-tune a pre-trained CNN on the dataset
3. Implement post-processing for actionable insights
4. Optimize for mobile deployment

### 2. Pathogen Spread Prediction Model

**Purpose:** Predict how detected pathogens will spread over time

**Suggested Approach:**
- **Architecture:** Combined LSTM and spatial CNN as implemented in `src/models/spread_prediction.py`
- **Training Data:** Historical spread patterns, weather data, and geographic features
- **Features:**
  - Temporal-spatial prediction
  - Environmental factor consideration
  - Confidence degradation over time
  - Multiple scenario generation

**Implementation Path:**
1. Enhance the existing LSTM model with attention mechanisms
2. Incorporate weather API data as additional features
3. Validate with historical outbreak data
4. Implement uncertainty quantification

### 3. Companion Planting Optimizer

**Purpose:** Generate optimal companion planting strategies

**Suggested Approach:**
- **Architecture:** Reinforcement learning or genetic algorithm optimization
- **Training Data:** Plant interaction data, historical yield results, pest resistance outcomes
- **Features:**
  - Multi-objective optimization (yield, pest resistance, resource usage)
  - Constraint handling for climate and soil conditions
  - Compatibility scoring

**Implementation Path:**
1. Build a knowledge graph of plant interactions
2. Develop an optimization algorithm that maximizes positive interactions
3. Incorporate geographical and climate constraints
4. Validate against known successful companion planting patterns

### 4. Early Warning Anomaly Detection

**Purpose:** Identify unusual patterns in sensor data that might indicate emerging threats

**Suggested Approach:**
- **Architecture:** Autoencoder or One-Class SVM for anomaly detection
- **Training Data:** Normal sensor readings across different conditions
- **Features:**
  - Unsupervised learning to detect deviations
  - Sensor fusion from multiple data sources
  - Adaptive thresholds based on environmental conditions

**Implementation Path:**
1. Train models on "normal" agricultural conditions
2. Implement real-time scoring of incoming sensor data
3. Create adaptive alerting thresholds
4. Develop feedback mechanisms to improve detection accuracy

### User Feedback Loop
- Add rating system for recommendation effectiveness
- Implement follow-up notifications to track implementation success
- Create community sharing of successful defense strategies

### Mobile Optimization
- Create mobile-friendly interfaces for field use
- Implement offline capabilities for areas with limited connectivity
- Develop lightweight ML models for on-device processing

## Contributing

Contributions to AgriDefender are welcome! Please see our contributing guidelines for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Research concepts derived from the Agricultural Defense Hackathon
- Special thanks to all contributors and agricultural domain experts

## Usage Examples

### Submitting Sensor Data

```python
import requests
import json

# Example soil sensor data
soil_data = {
    "data": {
        "sensor_id": "sensor-001",
        "timestamp": "2025-04-26T15:30:45Z",
        "location": {
            "type": "Point",
            "coordinates": [-97.7431, 30.2672]
        },
        "sensor_type": "SOIL",
        "moisture": 65.0,
        "ph": 5.5,
        "temperature": 24.3,
        "nitrogen": 40.2,
        "phosphorus": 22.8,
        "potassium": 120.6
    }
}

response = requests.post(
    "http://localhost:8000/api/v1/sensors/data", 
    json=soil_data
)
print(response.json())
```

### Querying Threats

```python
import requests

# Get all HIGH severity threats
response = requests.get(
    "http://localhost:8000/api/v1/threats",
    params={"threat_level": "HIGH"}
)

threats = response.json()
for threat in threats:
    print(f"ID: {threat['id']}")
    print(f"Type: {threat['threat_type']}")
    print(f"Level: {threat['threat_level']}")
    print(f"Confidence: {threat['confidence']:.2f}")
    print(f"Description: {threat['description']}")
    print("Recommendations:")
    for rec in threat['recommendations']:
        print(f"- {rec}")
    print("-" * 50)
```

### Running a Prediction Model

```python
from src.models.spread_prediction import PathogenSpreadModel
import numpy as np
import matplotlib.pyplot as plt

# Load the model
model = PathogenSpreadModel.load_model("models/latest_model.h5")

# Run a prediction
initial_state = np.load("data/initial_state.npy")
predictions = model.predict_spread(
    initial_state=initial_state,
    time_steps=7  # Predict 7 days ahead
)

# Generate a heatmap
heatmap = model.generate_probability_heatmap(predictions)
model.plot_heatmap(heatmap, save_path="output/heatmap.png")
```
