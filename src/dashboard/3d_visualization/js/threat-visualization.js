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
    
    // Create a 3D bubble (hemisphere) for the affected area
    const bubbleRadius = radius * 1.5; // Make bubbles larger for better visibility
    const bubbleGeometry = new THREE.SphereGeometry(bubbleRadius, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2);
    
    // Get color based on threat type with brighter, more saturated colors
    let color, emissiveColor;
    switch (threat.type) {
        case 'Fungal':
            color = 0xAE30E0; // Brighter purple
            emissiveColor = 0x9C27B0;
            break;
        case 'Bacterial':
            color = 0xFF5252; // Brighter red
            emissiveColor = 0xF44336;
            break;
        case 'Viral':
            color = 0xFFAB40; // Brighter orange
            emissiveColor = 0xFF9800;
            break;
        case 'Pest':
            color = 0x69F0AE; // Brighter green
            emissiveColor = 0x4CAF50;
            break;
        default:
            color = 0xFFFFFF;
            emissiveColor = 0xCCCCCC;
    }
    
    // Create advanced material with glass-like appearance for the bubble
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
    
    // Create bubble mesh and position it
    const bubble = new THREE.Mesh(bubbleGeometry, bubbleMaterial);
    bubble.position.set(threat.location.x, bubbleRadius * 0.15, threat.location.z); // Slightly raised
    
    // Add enhanced animation data and all threat data to make bubbles clickable
    bubble.userData = {
        isAffectedArea: true,
        isThreat: true, // Mark as threat to enable click handling
        threatId: threat.id,
        id: threat.id,
        name: threat.name,
        type: threat.type,
        severity: threat.severity,
        location: threat.location,
        detectedDate: threat.detectedDate,
        affectedArea: threat.affectedArea,
        description: threat.description || `This is a ${threat.severity.toLowerCase()} severity ${threat.type.toLowerCase()} threat affecting crops in this area.`,
        pulseAnimation: {
            speed: 0.005, // Faster animation
            minOpacity: 0.3,
            maxOpacity: 0.7,
            minScale: 0.9,  // Add scale pulsing
            maxScale: 1.15, 
            time: Math.random() * Math.PI * 2 // Random start phase
        }
    };
    
    // Start pulsing animation
    animateAffectedArea(bubble);
    
    // Add bubble to scene
    sceneRef.add(bubble);
    
    // Also create a ground circle for better context
    const circleGeometry = new THREE.CircleGeometry(radius, 32);
    const circleMaterial = new THREE.MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.3,
        side: THREE.DoubleSide
    });
    
    const circle = new THREE.Mesh(circleGeometry, circleMaterial);
    circle.rotation.x = -Math.PI / 2; // Rotate to lay flat on the ground
    circle.position.set(threat.location.x, 0.05, threat.location.z); // Slightly above ground
    
    // Add to scene
    sceneRef.add(circle);
    
    // Add both to tracking map
    activeThreats.set(`${threat.id}-bubble`, bubble);
    activeThreats.set(`${threat.id}-ground`, circle);
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
        
        // Calculate sine wave value (0 to 1)
        const sineWave = (Math.sin(pulse.time) * 0.5 + 0.5);
        
        // Pulsing opacity
        if (pulse.minOpacity && pulse.maxOpacity) {
            const opacityRange = pulse.maxOpacity - pulse.minOpacity;
            areaObj.material.opacity = pulse.minOpacity + sineWave * opacityRange;
        }
        
        // Pulsing scale for 3D bubbles
        if (areaObj.geometry.type === 'SphereGeometry' && pulse.minScale && pulse.maxScale) {
            const scale = pulse.minScale + (pulse.maxScale - pulse.minScale) * sineWave;
            areaObj.scale.set(scale, scale, scale);
            
            // Add subtle bobbing motion
            areaObj.position.y = areaObj.position.y + Math.sin(pulse.time * 0.7) * 0.05;
        }
        
        requestAnimationFrame(animate);
    };
    
    animate();
}

// Export functions
export {
    initializeThreatVisualization,
    updateThreats
};
