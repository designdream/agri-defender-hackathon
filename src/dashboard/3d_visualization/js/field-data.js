// field-data.js - Manages field and crop data

// Field class to represent agricultural fields
class Field {
    constructor(id, name, width, height, crops = [], threats = [], sensors = [], drones = [], satelliteData = {}) {
        this.id = id;
        this.name = name;
        this.width = width;
        this.height = height;
        this.crops = crops;
        this.threats = threats;
        this.sensors = sensors;
        this.drones = drones;
        this.satelliteData = satelliteData;
    }
}

// Mock data for fields (in production, this would come from an API)
const mockFields = {
    field1: {
        id: 'field1',
        name: 'North Wheat Field',
        width: 100,
        height: 100,
        cropType: 'wheat',
        cropDensity: 0.3,
        threatCount: 12,
        sensorCount: 8,
        dronePatrol: true,
        cropPattern: 'grid',
        cropVarieties: ['wheat-standard', 'wheat-sentinel'],
        sensorTypes: ['soil', 'weather', 'voc'],
        satelliteData: {
            lastUpdate: '2025-04-25',
            provider: 'Sentinel-2',
            resolution: '10m',
            bands: ['RGB', 'NIR', 'SWIR'],
            ndviAverage: 0.72,
            imageUrl: 'https://i.imgur.com/TvC5zcD.jpg'
        }
    },
    field2: {
        id: 'field2',
        name: 'South Corn Field',
        width: 80,
        height: 120,
        cropType: 'corn',
        cropDensity: 0.25,
        threatCount: 8,
        sensorCount: 12,
        dronePatrol: true,
        cropPattern: 'rows',
        cropVarieties: ['corn-standard', 'corn-bt'],
        sensorTypes: ['soil', 'acoustic', 'thermal'],
        satelliteData: {
            lastUpdate: '2025-04-26',
            provider: 'Drone Imagery',
            resolution: '5cm',
            bands: ['RGB', 'Thermal'],
            ndviAverage: 0.68,
            imageUrl: 'https://i.imgur.com/f3dvOUX.jpg'
        }
    },
    field3: {
        id: 'field3',
        name: 'East Orchard',
        width: 120,
        height: 120,
        cropType: 'apple',
        cropDensity: 0.15,
        threatCount: 5,
        sensorCount: 15,
        dronePatrol: true,
        cropPattern: 'scattered',
        cropVarieties: ['apple-honeycrisp', 'apple-gala', 'pear-bartlett'],
        sensorTypes: ['soil', 'weather', 'moisture', 'acoustic'],
        satelliteData: {
            lastUpdate: '2025-04-24',
            provider: 'Planet SkySat',
            resolution: '0.5m',
            bands: ['RGB', 'NIR'],
            ndviAverage: 0.81,
            imageUrl: 'https://i.imgur.com/5VtMqSB.jpg'
        }
    }
};

// Get list of available fields
function getFieldList() {
    return Object.values(mockFields).map(field => ({
        id: field.id,
        name: field.name,
        threatCount: field.threatCount
    }));
}

// Generate crops based on field parameters
function generateCrops(field) {
    const crops = [];
    const { width, height, cropType, cropDensity, cropPattern, cropVarieties } = field;
    const halfWidth = width / 2;
    const halfHeight = height / 2;
    
    // Calculate grid parameters
    const spacing = cropType === 'tree' ? 10 : 5;
    const rowSpacing = cropType === 'corn' ? 6 : spacing;
    const jitter = cropType === 'tree' ? 2 : 1; // Random position variation
    
    // Pattern configurations
    let patternFunc;
    
    switch(cropPattern || 'grid') {
        case 'rows':
            patternFunc = (x, z) => Math.abs(x % 20) < 15; // Create row gaps every 20 units
            break;
        case 'scattered':
            patternFunc = () => Math.random() < 0.7; // More randomized placement
            break;
        case 'blocks':
            patternFunc = (x, z) => (Math.floor(x / 20) + Math.floor(z / 20)) % 2 === 0; // Checkered blocks
            break;
        case 'grid':
        default:
            patternFunc = () => true; // Regular grid pattern
    }
    
    // Generate crops according to the selected pattern
    for (let x = -halfWidth + spacing; x < halfWidth - spacing; x += spacing) {
        for (let z = -halfHeight + rowSpacing; z < halfHeight - rowSpacing; z += rowSpacing) {
            // Apply pattern function and density
            if (patternFunc(x, z) && Math.random() > (1 - cropDensity)) {
                // Determine crop variety
                let variety = cropType;
                if (cropVarieties && cropVarieties.length > 0) {
                    // Use sentinel plants along the perimeter for early detection
                    const isPerimeter = 
                        Math.abs(x) > halfWidth - spacing * 3 || 
                        Math.abs(z) > halfHeight - rowSpacing * 3;
                    
                    if (isPerimeter && cropVarieties.some(v => v.includes('sentinel'))) {
                        // Use sentinel variety on perimeter
                        variety = cropVarieties.find(v => v.includes('sentinel'));
                    } else {
                        // Random variety selection with main variety being more common
                        const randomIndex = Math.random() < 0.8 ? 0 : 
                            Math.floor(Math.random() * cropVarieties.length);
                        variety = cropVarieties[randomIndex] || cropType;
                    }
                }
                
                const crop = {
                    type: cropType,
                    variety: variety,
                    x: x + (Math.random() * jitter * 2 - jitter),
                    z: z + (Math.random() * jitter * 2 - jitter),
                    scale: 0.8 + Math.random() * 0.4, // Random scale variation
                    rotation: Math.random() * Math.PI * 2, // Random rotation
                    health: Math.random() < 0.9 ? 'healthy' : 'stressed' // Most plants healthy, some stressed
                };
                crops.push(crop);
            }
        }
    }
    
    return crops;
}

// Generate threat data for a field
function generateThreats(field) {
    const threats = [];
    const { width, height, threatCount } = field;
    const halfWidth = width / 2;
    const halfHeight = height / 2;
    
    // Threat types and severity levels
    const threatTypes = ['Fungal', 'Bacterial', 'Viral', 'Pest'];
    const severityLevels = ['Low', 'Medium', 'High'];
    
    // Names for each threat type
    const threatNames = {
        Fungal: ['Rust', 'Powdery Mildew', 'Leaf Blight', 'Root Rot', 'Smut'],
        Bacterial: ['Bacterial Wilt', 'Fire Blight', 'Leaf Spot', 'Crown Gall', 'Soft Rot'],
        Viral: ['Mosaic Virus', 'Ring Spot', 'Yellow Leaf Curl', 'Stunting Virus', 'Necrosis'],
        Pest: ['Aphids', 'Stem Borer', 'Leaf Miner', 'Whitefly', 'Root Nematode']
    };
    
    // Generate the specified number of threats
    for (let i = 0; i < threatCount; i++) {
        // Randomly select threat characteristics
        const type = threatTypes[Math.floor(Math.random() * threatTypes.length)];
        const severity = severityLevels[Math.floor(Math.random() * severityLevels.length)];
        const name = threatNames[type][Math.floor(Math.random() * threatNames[type].length)];
        
        // Random position within the field, staying away from the edges
        const x = Math.random() * (width - 20) - (width / 2 - 10);
        const z = Math.random() * (height - 20) - (height / 2 - 10);
        
        // Random affected area based on severity
        let affectedArea;
        if (severity === 'Low') {
            affectedArea = 5 + Math.floor(Math.random() * 10);
        } else if (severity === 'Medium') {
            affectedArea = 15 + Math.floor(Math.random() * 20);
        } else {
            affectedArea = 35 + Math.floor(Math.random() * 50);
        }
        
        // Generate a date between 1-30 days ago
        const daysAgo = Math.floor(Math.random() * 30) + 1;
        const detectedDate = new Date();
        detectedDate.setDate(detectedDate.getDate() - daysAgo);
        const formattedDate = detectedDate.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        });
        
        // Generate description based on type and severity
        const descriptions = {
            Fungal: {
                Low: "Early signs of fungal infection with minimal spread.",
                Medium: "Moderate fungal infection affecting multiple plants. Requires prompt treatment.",
                High: "Severe fungal infestation spreading rapidly across plants. Urgent intervention needed."
            },
            Bacterial: {
                Low: "Isolated bacterial infection with minor symptoms.",
                Medium: "Spreading bacterial infection with visible plant damage.",
                High: "Critical bacterial outbreak affecting large areas. May lead to significant crop loss."
            },
            Viral: {
                Low: "Early viral symptoms detected in a few plants.",
                Medium: "Viral infection spreading through the field with clear symptoms.",
                High: "Severe viral outbreak with systemic plant damage. High risk of complete crop failure."
            },
            Pest: {
                Low: "Small pest population detected with minimal plant damage.",
                Medium: "Growing pest infestation affecting multiple plants.",
                High: "Critical pest outbreak with extensive damage. Requires immediate treatment."
            }
        };
        
        // Create the threat object
        const threat = {
            id: `threat-${field.id}-${i}`,
            name: name,
            type: type,
            severity: severity,
            location: { x, z },
            detectedDate: formattedDate,
            daysAgo: daysAgo,
            affectedArea: affectedArea,
            description: descriptions[type][severity],
            isThreat: true
        };
        
        threats.push(threat);
    }
    
    return threats;
}

// Generate sensors for the field
function generateSensors(field) {
    const sensors = [];
    const { width, height, sensorCount, sensorTypes } = field;
    const halfWidth = width / 2;
    const halfHeight = height / 2;
    
    // If no sensor data, return empty array
    if (!sensorCount || !sensorTypes || sensorTypes.length === 0) {
        return sensors;
    }
    
    // Sensor type configurations
    const sensorConfigs = {
        'soil': { height: 0.5, color: 0x8D6E63, shape: 'cylinder', radius: 0.3 },
        'weather': { height: 2.5, color: 0x03A9F4, shape: 'pole', radius: 0.2 },
        'voc': { height: 1.2, color: 0x9C27B0, shape: 'sphere', radius: 0.4 },
        'acoustic': { height: 2.0, color: 0xFF9800, shape: 'cone', radius: 0.3 },
        'thermal': { height: 1.8, color: 0xF44336, shape: 'box', radius: 0.25 },
        'spectral': { height: 1.5, color: 0x4CAF50, shape: 'pyramid', radius: 0.35 }
    };
    
    // Create strategic sensor placement
    // 1. Perimeter sensors
    const perimeterPoints = [
        // Corners
        { x: -halfWidth + 10, z: -halfHeight + 10 },
        { x: -halfWidth + 10, z: halfHeight - 10 },
        { x: halfWidth - 10, z: -halfHeight + 10 },
        { x: halfWidth - 10, z: halfHeight - 10 },
        // Mid-points
        { x: 0, z: -halfHeight + 10 },
        { x: 0, z: halfHeight - 10 },
        { x: -halfWidth + 10, z: 0 },
        { x: halfWidth - 10, z: 0 }
    ];
    
    // 2. Add sensors at strategic points first
    perimeterPoints.slice(0, Math.min(sensorCount, perimeterPoints.length)).forEach((point, i) => {
        const typeIndex = i % sensorTypes.length;
        const sensorType = sensorTypes[typeIndex];
        const config = sensorConfigs[sensorType] || sensorConfigs.soil;
        
        sensors.push({
            type: sensorType,
            x: point.x,
            z: point.z,
            height: config.height,
            color: config.color,
            shape: config.shape,
            radius: config.radius,
            status: Math.random() < 0.9 ? 'active' : 'maintenance',
            data: {
                lastReading: new Date().toISOString(),
                batteryLevel: 50 + Math.floor(Math.random() * 50),
                readings: generateSensorReadings(sensorType)
            }
        });
    });
    
    // 3. Add remaining sensors randomly across the field
    const remainingSensors = sensorCount - sensors.length;
    for (let i = 0; i < remainingSensors; i++) {
        const typeIndex = i % sensorTypes.length;
        const sensorType = sensorTypes[typeIndex];
        const config = sensorConfigs[sensorType] || sensorConfigs.soil;
        
        // Random position, but avoid edges
        const x = Math.random() * (width - 20) - (width/2 - 10);
        const z = Math.random() * (height - 20) - (height/2 - 10);
        
        sensors.push({
            type: sensorType,
            x,
            z,
            height: config.height,
            color: config.color,
            shape: config.shape,
            radius: config.radius,
            status: Math.random() < 0.9 ? 'active' : 'maintenance',
            data: {
                lastReading: new Date().toISOString(),
                batteryLevel: 50 + Math.floor(Math.random() * 50),
                readings: generateSensorReadings(sensorType)
            }
        });
    }
    
    return sensors;
}

// Generate mock readings for sensors
function generateSensorReadings(sensorType) {
    let readings = {};
    
    switch (sensorType) {
        case 'soil':
            readings = {
                moisture: Math.floor(Math.random() * 100),
                ph: (5 + Math.random() * 3).toFixed(1),
                temperature: (15 + Math.random() * 15).toFixed(1),
                nutrientIndex: Math.floor(50 + Math.random() * 50)
            };
            break;
        case 'weather':
            readings = {
                temperature: (15 + Math.random() * 20).toFixed(1),
                humidity: Math.floor(Math.random() * 100),
                windSpeed: (Math.random() * 20).toFixed(1),
                rainfall: (Math.random() * 5).toFixed(2)
            };
            break;
        case 'voc':
            readings = {
                ethylene: Math.floor(Math.random() * 100),
                methane: Math.floor(Math.random() * 50),
                ammonia: Math.floor(Math.random() * 30),
                stressIndex: Math.floor(Math.random() * 100)
            };
            break;
        case 'acoustic':
            readings = {
                pestActivity: Math.floor(Math.random() * 100),
                frequencyPeaks: Math.floor(1 + Math.random() * 5),
                intensityLevel: Math.floor(Math.random() * 100)
            };
            break;
        case 'thermal':
            readings = {
                surfaceTemp: (15 + Math.random() * 25).toFixed(1),
                tempVariation: (Math.random() * 5).toFixed(1),
                heatStressIndex: Math.floor(Math.random() * 100)
            };
            break;
        case 'spectral':
            readings = {
                ndvi: (0.2 + Math.random() * 0.6).toFixed(2),
                chlorophyllIndex: Math.floor(50 + Math.random() * 50),
                waterStressIndex: Math.floor(Math.random() * 100)
            };
            break;
    }
    
    return readings;
}

// Generate patrol drones for the field
function generateDrones(field) {
    const drones = [];
    
    if (!field.dronePatrol) {
        return drones;
    }
    
    const { width, height } = field;
    const halfWidth = width / 2;
    const halfHeight = height / 2;
    
    // Create patrol paths
    const paths = [
        // Perimeter patrol
        [
            { x: -halfWidth + 15, z: -halfHeight + 15, y: 15 },
            { x: halfWidth - 15, z: -halfHeight + 15, y: 15 },
            { x: halfWidth - 15, z: halfHeight - 15, y: 15 },
            { x: -halfWidth + 15, z: halfHeight - 15, y: 15 }
        ],
        // Cross patrol
        [
            { x: -halfWidth + 15, z: -halfHeight + 15, y: 20 },
            { x: halfWidth - 15, z: halfHeight - 15, y: 20 }
        ],
        // Scan pattern
        [
            { x: -halfWidth + 15, z: 0, y: 25 },
            { x: halfWidth - 15, z: 0, y: 25 }
        ]
    ];
    
    // Create 1-3 drones with different paths
    const droneCount = 1 + Math.floor(Math.random() * 2);
    for (let i = 0; i < droneCount; i++) {
        const pathIndex = i % paths.length;
        const speed = 0.2 + Math.random() * 0.3;
        const currentPointIndex = Math.floor(Math.random() * paths[pathIndex].length);
        const startPosition = paths[pathIndex][currentPointIndex];
        
        drones.push({
            id: `drone-${field.id}-${i}`,
            name: `Pathogen Radar ${i+1}`,
            type: i === 0 ? 'scanner' : (i === 1 ? 'sprayer' : 'sampler'),
            position: { ...startPosition },
            path: paths[pathIndex],
            currentPointIndex,
            speed,
            status: Math.random() < 0.9 ? 'active' : 'charging',
            batteryLevel: 30 + Math.floor(Math.random() * 70),
            sensors: ['hyperspectral', 'thermal', 'rgb'].slice(0, 1 + Math.floor(Math.random() * 2))
        });
    }
    
    return drones;
}

// Load field data (in production, this would fetch from an API)
async function loadFieldData(fieldId) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Get field from mock data
    const fieldData = mockFields[fieldId];
    
    if (!fieldData) {
        console.error(`Field with ID ${fieldId} not found`);
        return null;
    }
    
    // Generate crops and threats for the field
    const crops = generateCrops(fieldData);
    const threats = generateThreats(fieldData);
    const sensors = generateSensors(fieldData);
    const drones = generateDrones(fieldData);
    
    // Create and return the Field object
    return new Field(
        fieldData.id,
        fieldData.name,
        fieldData.width,
        fieldData.height,
        crops,
        threats,
        sensors,
        drones
    );
}

// Export functions and classes
export {
    Field,
    loadFieldData,
    getFieldList
};
