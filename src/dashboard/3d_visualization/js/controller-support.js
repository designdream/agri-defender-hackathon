// controller-support.js - 8BitDo Micro Controller Support for AgriDefender 3D
// This module provides support for the 8BitDo Micro gaming controller in keyboard mode
// and integrates it with the defense system navigation

// Controller state
const controllerState = {
    connected: false,
    axes: [0, 0, 0, 0],  // Left stick X, Left stick Y, Right stick X, Right stick Y
    buttons: {
        up: false,       // D-pad Up
        down: false,     // D-pad Down
        left: false,     // D-pad Left
        right: false,    // D-pad Right
        a: false,        // A button (Cross)
        b: false,        // B button (Circle)
        x: false,        // X button (Square)
        y: false,        // Y button (Triangle)
        l1: false,       // L1 button (Left shoulder)
        r1: false,       // R1 button (Right shoulder)
        l2: false,       // L2 button (Left trigger)
        r2: false,       // R2 button (Right trigger)
        select: false,   // Select button
        start: false,    // Start button
        l3: false,       // L3 button (Left stick press)
        r3: false        // R3 button (Right stick press)
    },
    // Keyboard mapping for 8BitDo Micro in keyboard mode
    keyMapping: {
        'ArrowUp': 'up',
        'ArrowDown': 'down',
        'ArrowLeft': 'left',
        'ArrowRight': 'right',
        'KeyZ': 'a',      // B on controller
        'KeyX': 'b',      // A on controller
        'KeyA': 'x',      // Y on controller
        'KeyS': 'y',      // X on controller
        'KeyQ': 'l1',     // L on controller
        'KeyW': 'r1',     // R on controller
        'KeyC': 'select', // Select on controller
        'KeyV': 'start',  // Start on controller
        'KeyD': 'l2',     // ZL on controller 
        'KeyF': 'r2'      // ZR on controller
    }
};

// Camera movement configuration
const cameraConfig = {
    moveSpeed: 0.5,      // Base movement speed
    sprintMultiplier: 2, // Speed multiplier when sprint is active
    rotateSpeed: 0.03,   // Rotation speed
    elevationSpeed: 0.3  // Vertical movement speed
};

// Initialize controller support
function initializeControllerSupport(camera, controls, scene) {
    // Create a local reference so we don't modify the original objects
    const refs = { 
        camera: camera, 
        controls: controls, 
        scene: scene 
    };
    
    // Set up event listeners for keyboard inputs (8BitDo Micro in keyboard mode)
    document.addEventListener('keydown', (event) => handleKeyEvent(event, true, refs));
    document.addEventListener('keyup', (event) => handleKeyEvent(event, false, refs));
    
    // Try to detect gamepad API for direct controller support when possible
    window.addEventListener('gamepadconnected', (event) => {
        console.log('Gamepad connected:', event.gamepad.id);
        controllerState.connected = true;
        
        // Show controller connected notification
        showControllerNotification('8BitDo Micro Controller Connected');
    });
    
    window.addEventListener('gamepaddisconnected', (event) => {
        console.log('Gamepad disconnected:', event.gamepad.id);
        controllerState.connected = false;
    });
    
    // Start the controller update loop - delay slightly to ensure scene is fully initialized
    setTimeout(() => {
        requestAnimationFrame(() => updateController(refs));
        console.log('8BitDo Micro Controller Support Ready');
    }, 1000);
    
    // Show initialization message
    console.log('8BitDo Micro Controller Support Initialized');
    showControllerNotification('Controller Support Initialized');
}

// Handle keyboard events (for 8BitDo Micro in keyboard mode)
function handleKeyEvent(event, isKeyDown, refs) {
    // Check if key is mapped
    const button = controllerState.keyMapping[event.code];
    if (button) {
        // Update button state
        controllerState.buttons[button] = isKeyDown;
        
        // Prevent default browser behavior for these keys
        event.preventDefault();
    }
    
    // Handle analog stick emulation
    // In keyboard mode, the 8BitDo Micro maps the left stick to arrow keys
    if (button === 'up') controllerState.axes[1] = isKeyDown ? -1 : 0;
    if (button === 'down') controllerState.axes[1] = isKeyDown ? 1 : 0;
    if (button === 'left') controllerState.axes[0] = isKeyDown ? -1 : 0;
    if (button === 'right') controllerState.axes[0] = isKeyDown ? 1 : 0;
    
    // If opposing directions are pressed, prioritize the most recent
    if (controllerState.buttons.up && controllerState.buttons.down) {
        controllerState.axes[1] = isKeyDown && (button === 'up' || button === 'down') ? 
            (button === 'up' ? -1 : 1) : 0;
    }
    if (controllerState.buttons.left && controllerState.buttons.right) {
        controllerState.axes[0] = isKeyDown && (button === 'left' || button === 'right') ? 
            (button === 'left' ? -1 : 1) : 0;
    }
}

// Process controller input for camera movement
function processCameraMovement(refs) {
    const { camera, controls } = refs;
    
    // Skip if no camera or controls are available
    if (!camera || !controls) return;
    
    // Get camera direction vectors
    const lookDirection = new THREE.Vector3();
    camera.getWorldDirection(lookDirection);
    
    // Create a normalized right vector from look direction
    const rightVector = new THREE.Vector3().crossVectors(lookDirection, camera.up).normalize();
    
    // Create a normalized forward vector (remove any y component for consistent forward movement)
    const forwardVector = new THREE.Vector3(lookDirection.x, 0, lookDirection.z).normalize();
    
    // Create new vectors for position changes without directly modifying camera
    let moveVector = new THREE.Vector3(0, 0, 0);
    
    // Check if sprint is active (R1 button)
    const speedMultiplier = controllerState.buttons.r1 ? cameraConfig.sprintMultiplier : 1;
    const currentSpeed = cameraConfig.moveSpeed * speedMultiplier;
    
    // Move forward/backward (left stick Y-axis)
    if (controllerState.axes[1] !== 0) {
        moveVector.add(forwardVector.clone().multiplyScalar(-controllerState.axes[1] * currentSpeed));
    }
    
    // Move left/right (left stick X-axis)
    if (controllerState.axes[0] !== 0) {
        moveVector.add(rightVector.clone().multiplyScalar(controllerState.axes[0] * currentSpeed));
    }
    
    // Elevation control (X/B buttons on 8BitDo)
    if (controllerState.buttons.y) { // Up (X button on 8BitDo)
        moveVector.y += cameraConfig.elevationSpeed;
    }
    if (controllerState.buttons.a) { // Down (B button on 8BitDo)
        moveVector.y -= cameraConfig.elevationSpeed;
    }
    
    // Apply movement
    if (moveVector.length() > 0) {
        camera.position.add(moveVector);
    }
    
    // Rotation (L1/R2 buttons)
    if (controllerState.buttons.l1) { // Rotate left
        camera.rotateY(cameraConfig.rotateSpeed);
    }
    if (controllerState.buttons.r2) { // Rotate right
        camera.rotateY(-cameraConfig.rotateSpeed);
    }
    
    // Update controls target to match camera position + look direction
    if (controls && moveVector.length() > 0) {
        controls.target.copy(camera.position.clone().add(lookDirection.multiplyScalar(1)));
        controls.update();
    }
}

// Main controller update loop
function updateController(refs) {
    // For direct gamepad API when available
    if (navigator.getGamepads) {
        const gamepads = navigator.getGamepads();
        for (const gamepad of gamepads) {
            if (gamepad && gamepad.id && gamepad.id.includes('8BitDo')) {
                updateGamepadState(gamepad);
                break;
            }
        }
    }
    
    try {
        // Process camera movement based on controller state
        if (refs.camera && refs.controls && (controllerState.connected || anyButtonPressed())) {
            processCameraMovement(refs);
        }
        
        // Process button actions for agricultural defense system
        processDefenseSystemActions(refs);
    } catch (error) {
        console.error('Controller update error:', error);
    }
    
    // Continue the loop
    requestAnimationFrame(() => updateController(refs));
}

// Update gamepad state from direct Gamepad API
function updateGamepadState(gamepad) {
    // Update axes (analog sticks)
    if (gamepad.axes.length >= 4) {
        for (let i = 0; i < 4; i++) {
            // Apply deadzone
            controllerState.axes[i] = Math.abs(gamepad.axes[i]) > 0.1 ? gamepad.axes[i] : 0;
        }
    }
    
    // Update buttons
    if (gamepad.buttons.length >= 16) {
        const buttonMapping = [
            'a', 'b', 'x', 'y',
            'l1', 'r1', 'l2', 'r2',
            'select', 'start',
            'l3', 'r3',
            'up', 'down', 'left', 'right'
        ];
        
        for (let i = 0; i < buttonMapping.length; i++) {
            if (i < gamepad.buttons.length) {
                controllerState.buttons[buttonMapping[i]] = gamepad.buttons[i].pressed;
            }
        }
    }
}

// Process button actions specific to agricultural defense system
function processDefenseSystemActions(refs) {
    const { scene } = refs;
    
    // Switch to Overhead View (Select button)
    if (controllerState.buttons.select && !prevButtonState.select) {
        setViewMode('overhead');
    }
    
    // Switch to First Person View (Start button)
    if (controllerState.buttons.start && !prevButtonState.start) {
        setViewMode('firstPerson');
    }
    
    // Selection/interaction with agricultural threats (A button)
    if (controllerState.buttons.b && !prevButtonState.b) {
        interactWithTargetedElement(scene);
    }
    
    // Store previous button state for edge detection
    Object.keys(controllerState.buttons).forEach(key => {
        prevButtonState[key] = controllerState.buttons[key];
    });
}

// Helper to set view mode
function setViewMode(mode) {
    const buttons = document.querySelectorAll('.view-mode-controls .control-btn');
    buttons.forEach(btn => {
        if (btn.dataset.mode === mode) {
            btn.click();
        }
    });
}

// Store previous button state for edge detection (pressed/released)
const prevButtonState = { ...controllerState.buttons };

// Check if any button is currently pressed
function anyButtonPressed() {
    return Object.values(controllerState.buttons).some(state => state);
}

// Simulate raycasting for interaction with agricultural elements
function interactWithTargetedElement(scene) {
    // Make sure we have the scene and camera from the global scope
    if (!scene || !window.camera) return;
    
    try {
        // Create a ray from camera center
        const raycaster = new THREE.Raycaster();
        raycaster.setFromCamera(new THREE.Vector2(0, 0), window.camera);
        
        // Find intersected objects
        const intersects = raycaster.intersectObjects(scene.children, true);
        
        // Process the first intersected object
        if (intersects.length > 0) {
            const object = findParentWithUserData(intersects[0].object);
            if (object && object.userData && object.userData.isThreat) {
                // Create a synthetic click event
                const clickEvent = new MouseEvent('click', {
                    clientX: window.innerWidth / 2,
                    clientY: window.innerHeight / 2
                });
                
                // Dispatch event to the document to be handled by the main click handler
                document.dispatchEvent(clickEvent);
            }
        }
    } catch (error) {
        console.error('Interaction error:', error);
    }
}

// Helper to find parent object with userData
function findParentWithUserData(object) {
    let current = object;
    while (current) {
        if (current.userData && Object.keys(current.userData).length > 0) {
            return current;
        }
        current = current.parent;
    }
    return null;
}

// Show controller notification
function showControllerNotification(message) {
    // Check if there's an existing toast system
    if (typeof showToast === 'function') {
        showToast(message);
        return;
    }
    
    // Create a simple notification if no toast system exists
    const notification = document.createElement('div');
    notification.className = 'controller-notification';
    notification.textContent = message;
    notification.style.position = 'absolute';
    notification.style.bottom = '20px';
    notification.style.left = '50%';
    notification.style.transform = 'translateX(-50%)';
    notification.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    notification.style.color = 'white';
    notification.style.padding = '10px 20px';
    notification.style.borderRadius = '5px';
    notification.style.zIndex = '1000';
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Export functions
export {
    initializeControllerSupport,
    controllerState
};
