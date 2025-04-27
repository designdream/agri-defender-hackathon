<div align="center">
  <img src="NARD.png" alt="NARD Logo" width="400"/>
  <h1>AgriDefender 3D - Agricultural Threat Visualization System</h1>
</div>

AgriDefender 3D is an immersive visualization system for detecting, monitoring, and responding to agricultural biological threats. Using Three.js 3D visualization, it provides farmers and agricultural authorities with an intuitive visual interface for protecting crops through interactive field visualization, automated drone patrols, threat identification, and sensor network monitoring.

## Project Overview

AgriDefender 3D provides an immersive and intuitive visualization platform with the following key features:

1. **3D Field Visualization** - Interactive, photorealistic representation of agricultural fields with crop health indicators
2. **Threat Detection & Representation** - Visually stunning 3D bubble visualization of detected threats with severity indicators
3. **Automated Drone Patrols** - Visual representation of autonomous drone flights for continuous monitoring
4. **Sensor Network Monitoring** - Interactive sensor placement and real-time data visualization
5. **Interactive Navigation** - First-person exploration using keyboard controls for immersive field inspection

## Architecture

The application is structured as follows:

```
├── src/
│   ├── dashboard/           
│   │   ├── 3d_visualization/  # Three.js 3D visualization
│   │   │   ├── js/           # JavaScript modules for visualization
│   │   │   │   ├── field-data.js        # Field, threat, drone & sensor data generation
│   │   │   │   ├── main.js              # Core Three.js setup and rendering
│   │   │   │   ├── threat-visualization.js # Threat visualization with 3D bubbles
│   │   │   │   └── ui-controls.js       # User interface and control handling
│   │   │   ├── index.html    # Main 3D visualization interface
│   │   │   └── styles.css    # Styling for the visualization interface
├── AgriDefender_3D.pdf       # Presentation slides
└── NARD.png                  # NARD logo
```

## Key Features

### 1. 3D Field Visualization

**Feature:** Interactive 3D representation of agricultural fields with accurately placed crops, boundaries, and terrain features.

**Implementation:**
- Technologies: Three.js, WebGL, GSAP animations
- Key files: `field-data.js`, `main.js`
- Features:
  - Photorealistic crop rendering
  - Terrain elevation and texture mapping
  - Day/night cycle with dynamic lighting
  - Multiple view modes (overhead, first-person, drone)

### 2. Interactive 3D Threat Bubbles

**Feature:** Visually striking 3D glass-like bubbles that represent detected threats on the field, with color-coding for different threat types.

**Implementation:**
- Technologies: Three.js MeshPhysicalMaterial with glass effects
- Key file: `threat-visualization.js`
- Features:
  - Pulsing animations with dynamic opacity and scale
  - Color coding by threat type (fungal, bacterial, viral, pest)
  - Clickable bubbles that reveal detailed threat information
  - Floating and bobbing effects for enhanced visibility

### 3. Automated Drone Patrol Visualization

**Feature:** Visual representation of autonomous drone flight paths and real-time monitoring activities.

**Implementation:**
- Key files: `main.js` (animateDrone function)
- Features:
  - Smooth path interpolation between waypoints
  - Animated rotors and realistic flight physics
  - Auto-orienting to direction of travel
  - Subtle bobbing motion for realism

### 4. Sensor Network

**Feature:** Interactive representation of field sensors that monitor environmental conditions and detect threats.

**Implementation:**
- Key files: `field-data.js` (sensor generation), `main.js` (renderSensors function)
- Features:
  - Multiple sensor types with distinctive models
  - Interactive tooltips showing sensor data
  - Visual indicators for sensor state

### 5. Immersive First-Person Navigation

**Feature:** Video game-style keyboard navigation allowing users to explore the field from a first-person perspective.

**Implementation:**
- Key files: `main.js` (keyboardControls)
- Controls:
  - WASD: Move forward/back/left/right
  - Q/E: Rotate left/right
  - Space/Shift: Move up/down
  - Ctrl: Sprint

## Getting Started

### Prerequisites

- Modern web browser with WebGL support (Chrome, Firefox, Edge recommended)
- Basic HTTP server capability (Python's built-in server or equivalent)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/designdream/agri-defender-hackathon.git
cd agri-defender-hackathon
```

2. Start a local web server:
```bash
python -m http.server 9000
```

3. Open your browser and navigate to:
```
http://localhost:9000/src/dashboard/3d_visualization/index.html
```

### Navigation

1. Use the View Mode controls to switch between Overhead, First Person, and Drone views
2. In First Person mode, use keyboard controls (WASD, Q/E, Space/Shift) to navigate
3. Click on 3D threat bubbles to view detailed information about detected threats
4. Click on sensors to see their current readings and status

## Technologies Used

- **Three.js**: Core 3D visualization engine for rendering fields, threats, drones, and sensors
- **JavaScript ES6+**: Modern JavaScript with modules for code organization
- **GSAP (GreenSock Animation Platform)**: Advanced animation for smooth transitions and effects
- **WebGL**: Hardware-accelerated graphics rendering for performance
- **CSS3**: Styling with advanced effects including backdrop filters
- **HTML5**: Semantic markup for the interface structure

## Technical Highlights

### Advanced Material Effects

The 3D threat bubbles use advanced Three.js MeshPhysicalMaterial properties to create realistic glass-like effects:

```javascript
const bubbleMaterial = new THREE.MeshPhysicalMaterial({
    color: color,
    transparent: true,
    opacity: 0.5,
    metalness: 0.2,
    roughness: 0.1,
    transmission: 0.8, // Glass-like transparency
    thickness: 0.8,    // Glass thickness
    envMapIntensity: 1.5,
    clearcoat: 1.0,
    clearcoatRoughness: 0.1,
    side: THREE.DoubleSide,
    emissive: emissiveColor, // Add glow
    emissiveIntensity: 0.3   // Subtle glow
});
```

### Animation System

All animations use request animation frame for performance and smooth movement, with time-based animations instead of frame-based for consistency across devices:

```javascript
function animateAffectedArea(areaObj) {
    // Calculate sine wave value for smooth oscillation
    const sineWave = (Math.sin(pulse.time) * 0.5 + 0.5);
    
    // Apply scale animation
    const scale = pulse.minScale + (pulse.maxScale - pulse.minScale) * sineWave;
    areaObj.scale.set(scale, scale, scale);
    
    // Add subtle bobbing motion
    areaObj.position.y = Math.sin(pulse.time * 0.7) * 0.05;
    
    requestAnimationFrame(animate);
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
