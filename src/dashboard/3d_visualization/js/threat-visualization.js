// threat-visualization.js - Handles threat visualization in 3D space

// References to scene and models
let sceneRef = null;
let threatModels = new Map();
let activeThreats = new Map();

// Initialize the threat visualization system
function initializeThreatVisualization(scene, loadedModels) {
    sceneRef = scene;
    
    // Store references to threat indicator models
    threatModels.set('Fungal', loadedModels.get('fungal'));
    threatModels.set('Bacterial', loadedModels.get('bacterial'));
    threatModels.set('Viral', loadedModels.get('viral'));
    threatModels.set('Pest', loadedModels.get('pest'));
}

// Update threats based on current app state 
function updateThreats(threats, appState) {
    if (!sceneRef || !threats) return;
    
    // Remove all current threats from scene
    clearThreats();
    
    // Filter threats based on app state
    const filteredThreats = threats.filter(threat => {
        // Filter by type
        if (!appState.selectedThreats[threat.type.toLowerCase()]) {
            return false;
        }
        
        // Filter by severity
        if (appState.activeThreatFilter !== 'all' && 
            threat.severity.toLowerCase() !== appState.activeThreatFilter) {
            return false;
        }
        
        // Filter by time
        if (threat.daysAgo > appState.timeRange) {
            return false;
        }
        
        return true;
    });
    
    // Add filtered threats to scene
    renderThreats(filteredThreats);
}

// Clear all threats from the scene
function clearThreats() {
    // Remove threat objects from scene
    activeThreats.forEach(threatObj => {
        if (threatObj && threatObj.parent === sceneRef) {
            sceneRef.remove(threatObj);
        }
    });
    
    // Clear the map
    activeThreats.clear();
}

// Render threats on the field
function renderThreats(threats) {
    threats.forEach(threat => {
        // Get the appropriate model for this threat type
        const modelTemplate = threatModels.get(threat.type);
        
        if (!modelTemplate) {
            console.error(`No model found for threat type: ${threat.type}`);
            return;
        }
        
        // Clone the model for this specific threat
        const threatInstance = modelTemplate.clone();
        
        // Position the threat
        threatInstance.position.set(threat.location.x, 1.5, threat.location.z);
        
        // Scale based on severity
        let scale = 1;
        switch (threat.severity.toLowerCase()) {
            case 'high':
                scale = 1.5;
                break;
            case 'medium':
                scale = 1;
                break;
            case 'low':
                scale = 0.7;
                break;
        }
        threatInstance.scale.set(scale, scale, scale);
        
        // Add hover animation
        const initialY = threatInstance.position.y;
        threatInstance.userData = {
            hover: {
                initialY: initialY,
                animation: {
                    speed: 0.005,
                    amplitude: 0.2,
                    time: Math.random() * Math.PI * 2 // Random start phase
                }
            },
            // Copy all threat data to the userData
            ...threat
        };
        
        // Start the animation loop for this threat
        animateThreat(threatInstance);
        
        // Add to scene and track in our map
        sceneRef.add(threatInstance);
        activeThreats.set(threat.id, threatInstance);
        
        // Add affected area visualization
        renderAffectedArea(threat);
    });
}

// Create visualization for the affected area
function renderAffectedArea(threat) {
    // Calculate radius from affected area (assuming circular area)
    const radius = Math.sqrt(threat.affectedArea / Math.PI);
    
    // Create a circular area marker on the ground
    const geometry = new THREE.CircleGeometry(radius, 32);
    
    // Get color based on threat type
    let color;
    switch (threat.type) {
        case 'Fungal':
            color = 0x9C27B0;
            break;
        case 'Bacterial':
            color = 0xF44336;
            break;
        case 'Viral':
            color = 0xFF9800;
            break;
        case 'Pest':
            color = 0x4CAF50;
            break;
        default:
            color = 0xFFFFFF;
    }
    
    // Create material with transparency
    const material = new THREE.MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.2,
        side: THREE.DoubleSide
    });
    
    // Create mesh and position it
    const circle = new THREE.Mesh(geometry, material);
    circle.rotation.x = -Math.PI / 2; // Rotate to lay flat on the ground
    circle.position.set(threat.location.x, 0.05, threat.location.z); // Slightly above ground
    
    // Add slight animation to the affected area
    circle.userData = {
        isAffectedArea: true,
        threatId: threat.id,
        pulseAnimation: {
            speed: 0.003,
            minOpacity: 0.1,
            maxOpacity: 0.3,
            time: Math.random() * Math.PI * 2 // Random start phase
        }
    };
    
    // Start pulsing animation
    animateAffectedArea(circle);
    
    // Add to scene
    sceneRef.add(circle);
    
    // Add to tracking map with compound ID
    activeThreats.set(`${threat.id}-area`, circle);
}

// Animate the threat indicator (floating effect)
function animateThreat(threatObj) {
    if (!threatObj || !threatObj.userData.hover) return;
    
    const animate = () => {
        if (!threatObj || !threatObj.parent) return; // Stop if threat is removed
        
        const hover = threatObj.userData.hover;
        hover.animation.time += hover.animation.speed;
        
        // Sinusoidal hover motion
        threatObj.position.y = hover.initialY + 
            Math.sin(hover.animation.time) * hover.animation.amplitude;
        
        // Slowly rotate
        threatObj.rotation.y += 0.01;
        
        requestAnimationFrame(animate);
    };
    
    animate();
}

// Animate the affected area (pulsing effect)
function animateAffectedArea(areaObj) {
    if (!areaObj || !areaObj.userData.pulseAnimation) return;
    
    const animate = () => {
        if (!areaObj || !areaObj.parent) return; // Stop if object is removed
        
        const pulse = areaObj.userData.pulseAnimation;
        pulse.time += pulse.speed;
        
        // Pulsing opacity
        const opacityRange = pulse.maxOpacity - pulse.minOpacity;
        areaObj.material.opacity = pulse.minOpacity + 
            (Math.sin(pulse.time) * 0.5 + 0.5) * opacityRange;
        
        requestAnimationFrame(animate);
    };
    
    animate();
}

// Export functions
export {
    initializeThreatVisualization,
    updateThreats
};
