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
}
```

## API Integration Guide

AgriDefender 3D is designed to integrate with real-world data sources through standardized APIs. This guide outlines the implementation details for connecting sensors, drones, and threat detection systems to the visualization platform.

### Sensor Data API

**Purpose:** Collect and process real-time data from field sensors for visualization.

**API Endpoints:**

```
GET /api/v1/sensors - List all sensors
GET /api/v1/sensors/{sensor_id} - Get specific sensor details
POST /api/v1/sensors/data - Submit new sensor reading
GET /api/v1/sensors/data/{sensor_id} - Get historical readings
```

**Data Format Example:**

```json
{
  "sensor_id": "soil-sensor-0042",
  "timestamp": "2025-04-27T17:30:22Z",
  "location": {"x": 156.3, "y": 0.3, "z": 78.2},
  "type": "SOIL",
  "readings": {
    "moisture": 37.8,
    "temperature": 22.5,
    "pH": 6.8,
    "nitrogen": 42,
    "conductivity": 0.38
  },
  "battery": 87,
  "status": "ACTIVE"
}
```

**Integration Implementation:**

```javascript
// In field-data.js
async function fetchSensorData() {
  try {
    const response = await fetch('https://api.agridefender.io/v1/sensors');
    if (!response.ok) throw new Error('Network response failed');
    
    const sensors = await response.json();
    return sensors.map(sensor => ({
      id: sensor.sensor_id,
      type: sensor.type,
      location: { x: sensor.location.x, y: sensor.location.y, z: sensor.location.z },
      readings: sensor.readings,
      status: sensor.status,
      lastUpdated: new Date(sensor.timestamp)
    }));
  } catch (error) {
    console.error('Error fetching sensor data:', error);
    return fallbackSensorData(); // Use local data if API fails
  }
}
```

### Drone Control API

**Purpose:** Monitor and control autonomous drones for field surveillance.

**API Endpoints:**

```
GET /api/v1/drones - List all drones
GET /api/v1/drones/{drone_id} - Get specific drone status
POST /api/v1/drones/{drone_id}/mission - Assign patrol mission
GET /api/v1/drones/{drone_id}/telemetry - Get real-time telemetry
```

**Data Format Example:**

```json
{
  "drone_id": "patrol-drone-007",
  "model": "AgriScout X2",
  "status": "PATROL",
  "battery": 76,
  "location": {"x": 423.1, "y": 45.8, "z": 216.4},
  "speed": 5.2,
  "heading": 283,
  "altitude": 45.8,
  "mission": {
    "id": "mission-2025-04-27-12",
    "type": "PATROL",
    "waypoints": [
      {"x": 400, "y": 45, "z": 200},
      {"x": 450, "y": 45, "z": 200},
      {"x": 450, "y": 45, "z": 250},
      {"x": 400, "y": 45, "z": 250}
    ],
    "progress": 68
  }
}
```

**Integration Implementation:**

```javascript
// In field-data.js
async function fetchDroneData() {
  try {
    const response = await fetch('https://api.agridefender.io/v1/drones');
    if (!response.ok) throw new Error('Network response failed');
    
    const drones = await response.json();
    return drones.map(drone => ({
      id: drone.drone_id,
      model: drone.model,
      status: drone.status,
      location: { x: drone.location.x, y: drone.location.y, z: drone.location.z },
      battery: drone.battery,
      patrolPath: drone.mission?.waypoints || [],
      currentWaypoint: Math.floor((drone.mission?.progress || 0) / 100 * 
                     (drone.mission?.waypoints?.length || 1))
    }));
  } catch (error) {
    console.error('Error fetching drone data:', error);
    return fallbackDroneData(); // Use local data if API fails
  }
}
```

### Threat Detection API

**Purpose:** Process and visualize detected agricultural threats.

**API Endpoints:**

```
GET /api/v1/threats - List all detected threats
GET /api/v1/threats/{threat_id} - Get specific threat details
POST /api/v1/threats - Report a new threat
PUT /api/v1/threats/{threat_id}/status - Update threat status
```

**Data Format Example:**

```json
{
  "threat_id": "threat-2025-04-27-036",
  "name": "Powdery Mildew Infection",
  "type": "Fungal",
  "severity": "High",
  "location": {"x": 256.7, "y": 0.2, "z": 189.3},
  "affectedArea": 78.5,
  "detectedDate": "2025-04-27T09:45:18Z",
  "detectionMethod": "SENSOR",
  "detectedBy": "soil-sensor-0028",
  "confidence": 0.94,
  "status": "ACTIVE",
  "progression": 0.35,
  "description": "White powdery substances on crop leaves with signs of spreading to nearby plants.",
  "recommendedActions": [
    "Apply organic fungicide immediately",
    "Increase plant spacing in affected area",
    "Reduce overhead irrigation"
  ]
}
```

**Integration Implementation:**

```javascript
// In threat-visualization.js
async function fetchThreatData() {
  try {
    const response = await fetch('https://api.agridefender.io/v1/threats');
    if (!response.ok) throw new Error('Network response failed');
    
    const threats = await response.json();
    return threats.map(threat => ({
      id: threat.threat_id,
      name: threat.name,
      type: threat.type,
      severity: threat.severity,
      location: { x: threat.location.x, y: threat.location.y, z: threat.location.z },
      affectedArea: threat.affectedArea,
      detectedDate: threat.detectedDate,
      confidence: threat.confidence,
      status: threat.status,
      description: threat.description,
      recommendations: threat.recommendedActions
    }));
  } catch (error) {
    console.error('Error fetching threat data:', error);
    return fallbackThreatData(); // Use local data if API fails
  }
}
```

### Webhook Integration for Real-time Updates

For real-time updates, AgriDefender 3D uses WebSockets to receive push notifications when new data is available:

```javascript
// In main.js
function initializeRealTimeUpdates() {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const socket = new WebSocket(`${wsProtocol}//api.agridefender.io/v1/websocket`);
  
  socket.onopen = () => {
    console.log('WebSocket connection established');
    // Subscribe to relevant data channels
    socket.send(JSON.stringify({
      action: 'subscribe',
      channels: ['sensors', 'drones', 'threats']
    }));
  };
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Handle different types of updates
    switch (data.type) {
      case 'sensor_update':
        updateSensorData(data.payload);
        break;
      case 'drone_update':
        updateDronePosition(data.payload);
        break;
      case 'threat_detected':
        addNewThreat(data.payload);
        break;
      case 'threat_update':
        updateThreatStatus(data.payload);
        break;
    }
  };
  
  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  socket.onclose = () => {
    console.log('WebSocket connection closed');
    // Attempt to reconnect after a delay
    setTimeout(initializeRealTimeUpdates, 5000);
  };
}
```

## Future Enhancements

Planned features for future development:

1. **Real-time Data Integration**: Connect to actual field sensor APIs for live data visualization
2. **AI Threat Prediction**: Integrate machine learning models to predict threat spread
3. **VR Support**: Add WebXR API support for fully immersive VR field exploration
4. **Advanced Weather System**: Dynamic weather visualization with impact on threat development
5. **Collaborative Field Inspection**: Multi-user support for team-based field monitoring

## Acknowledgments

- NARD (National Agricultural Research Department) for providing support and direction
- Three.js community for development resources and examples
- Agricultural defense researchers for domain expertise

## License

This project is licensed under the MIT License - see the LICENSE file for details.


