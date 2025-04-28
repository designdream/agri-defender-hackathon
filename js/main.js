// Main.js - Core Three.js setup and rendering logic
import { loadFieldData, Field } from './field-data.js';
import { initializeThreatVisualization, updateThreats } from './threat-visualization.js';
import { initializeControls, handleControlEvents } from './ui-controls.js';
import { initializeControllerSupport, controllerState } from './controller-support.js';
import { loadSatelliteTexture } from './satellite-imagery.js';

// Main Three.js variables
let scene, camera, renderer, controls;
let clock, mixers = [];
let raycaster, mouse;

// Field and threat-related variables
let currentField = null;
let loadedModels = new Map();

// App state
const appState = {
    viewMode: 'overhead', // 'overhead', 'firstPerson', 'drone'
    timeRange: 7, // days
    selectedThreats: {
        fungal: true,
        bacterial: true, 
        viral: true,
        pest: true
    },
    activeThreatFilter: 'all', // 'all', 'high', 'medium', 'low'
    selectedFieldId: 'field1',
    isLoading: true,
    hoverObject: null,
    selectedObject: null
};

// Initialize the application
async function init() {
    showLoadingScreen(true);
    setupThreeJS();
    setupLighting();
    setupHelpers();
    initializeControls(appState, onControlsChanged);
    setupEventListeners();
    await loadModels();
    
    // Load field data 
    currentField = await loadFieldData(appState.selectedFieldId);
    
    // Create field visualization
    renderField(currentField);
    
    // Initialize threat visualization with loaded models
    initializeThreatVisualization(scene, loadedModels);
    
    // Update threat visualization based on initial state
    updateThreatVisibility();
    
    // Hide loading screen and begin animation loop
    showLoadingScreen(false);
    
    // Make camera and controls available globally for controller access
    window.camera = camera;
    
    // Wait until the scene is fully rendered before initializing controller support
    setTimeout(() => {
        // Initialize 8BitDo Micro controller support
        initializeControllerSupport(camera, controls, scene);
        showToast('8BitDo Micro Controller Support Activated');
    }, 2000);
    animate();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
}

// Set up the Three.js environment
function setupThreeJS() {
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87CEEB); // Sky blue background
    scene.fog = new THREE.FogExp2(0xC8E6C9, 0.005); // Subtle green-tinted fog
    
    // Create camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 20, 20); // Initial camera position
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('canvas-container').appendChild(renderer.domElement);
    
    // Create orbit controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = false;
    controls.minDistance = 5;
    controls.maxDistance = 50;
    controls.maxPolarAngle = Math.PI / 2; // Limit to not go below the ground
    
    // Initialize clock for animations
    clock = new THREE.Clock();
    
    // Set up raycaster for interaction
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
    
    // Handlers
    window.addEventListener('resize', onWindowResize);
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('click', onMouseClick);
}

// Setup additional event listeners
function setupEventListeners() {
    // Close threat info panel when close button is clicked
    const closeButton = document.querySelector('.threat-info-panel .close-panel');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            document.querySelector('.threat-info-panel').style.display = 'none';
            
            // Reset selection if there was one
            if (appState.selectedObject) {
                appState.selectedObject.traverse(child => {
                    if (child.isMesh && child._selectionColor) {
                        child.material.color.copy(child._selectionColor);
                        delete child._selectionColor;
                    }
                });
                appState.selectedObject = null;
            }
        });
    }
}

// Set up lighting for the scene
function setupLighting() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xFFFFFF, 0.5);
    scene.add(ambientLight);
    
    // Directional light (sun)
    const directionalLight = new THREE.DirectionalLight(0xFFFFFF, 0.8);
    directionalLight.position.set(-10, 20, 10);
    directionalLight.castShadow = true;
    
    // Adjust shadow properties
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 50;
    directionalLight.shadow.camera.left = -25;
    directionalLight.shadow.camera.right = 25;
    directionalLight.shadow.camera.top = 25;
    directionalLight.shadow.camera.bottom = -25;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    
    scene.add(directionalLight);
    
    // Hemisphere light (sky light)
    const hemisphereLight = new THREE.HemisphereLight(0x87CEEB, 0x689F38, 0.6);
    scene.add(hemisphereLight);
}

// Set up helper objects for development
function setupHelpers() {
    // Only add helpers if in development mode
    if (window.location.search.includes('debug=true')) {
        const axesHelper = new THREE.AxesHelper(10);
        scene.add(axesHelper);
        
        const gridHelper = new THREE.GridHelper(100, 100);
        scene.add(gridHelper);
    }
}

// Load 3D models
async function loadModels() {
    const modelLoader = new THREE.GLTFLoader();
    
    try {
        // Load crop models
        const cornPromise = loadModel(modelLoader, '/models/corn_plant.glb', 'corn');
        const wheatPromise = loadModel(modelLoader, '/models/wheat_plant.glb', 'wheat');
        const treePromise = loadModel(modelLoader, '/models/tree.glb', 'tree');
        
        // Load threat indicator models
        const fungalPromise = loadModel(modelLoader, '/models/fungal_indicator.glb', 'fungal');
        const bacterialPromise = loadModel(modelLoader, '/models/bacterial_indicator.glb', 'bacterial');
        const viralPromise = loadModel(modelLoader, '/models/viral_indicator.glb', 'viral');
        const pestPromise = loadModel(modelLoader, '/models/pest_indicator.glb', 'pest');
        
        // Wait for all models to load
        await Promise.all([
            cornPromise, wheatPromise, treePromise,
            fungalPromise, bacterialPromise, viralPromise, pestPromise
        ]);
        
        console.log('All models loaded successfully');
    } catch (error) {
        console.error('Error loading models:', error);
        
        // Use fallback geometries if models fail to load
        createFallbackModels();
    }
}

// Load a single model
async function loadModel(loader, path, name) {
    try {
        // For development/testing, we'll use placeholder geometries
        // In production, this would use the actual model path
        createFallbackModels(name);
        return Promise.resolve();
        
        /* Commented out for testing without actual models
        const gltf = await new Promise((resolve, reject) => {
            loader.load(
                path,
                (gltf) => resolve(gltf),
                (xhr) => console.log(`${name} ${(xhr.loaded / xhr.total) * 100}% loaded`),
                (error) => reject(error)
            );
        });
        
        // Store the loaded model
        loadedModels.set(name, gltf.scene);
        
        // Set up any animations if present
        if (gltf.animations && gltf.animations.length > 0) {
            const mixer = new THREE.AnimationMixer(gltf.scene);
            gltf.animations.forEach(animation => {
                mixer.clipAction(animation).play();
            });
            mixers.push(mixer);
        }
        */
    } catch (error) {
        console.error(`Error loading model ${name}:`, error);
        // Create a fallback geometry in case of error
        createFallbackModels(name);
    }
}

// Create fallback geometric models when 3D models can't be loaded
function createFallbackModels(specificModel = null) {
    const createModels = (modelType) => {
        if (specificModel && modelType !== specificModel && specificModel !== 'all') {
            return;
        }
        
        let geometry, material, mesh;
        
        switch (modelType) {
            case 'corn':
                geometry = new THREE.CylinderGeometry(0.2, 0.1, 2, 8);
                material = new THREE.MeshLambertMaterial({ color: 0x558B2F });
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.y = 1;
                break;
            
            case 'corn-standard':
                geometry = new THREE.CylinderGeometry(0.2, 0.1, 2, 8);
                material = new THREE.MeshLambertMaterial({ color: 0x558B2F });
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.y = 1;
                break;
                
            case 'corn-bt':
                geometry = new THREE.CylinderGeometry(0.25, 0.15, 2.2, 8);
                material = new THREE.MeshLambertMaterial({ color: 0x8BC34A });
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.y = 1.1;
                break;
                
            case 'wheat':
                geometry = new THREE.CylinderGeometry(0.1, 0.05, 1.5, 8);
                material = new THREE.MeshLambertMaterial({ color: 0xFDD835 });
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.y = 0.75;
                break;
                
            case 'wheat-standard':
                geometry = new THREE.CylinderGeometry(0.1, 0.05, 1.5, 8);
                material = new THREE.MeshLambertMaterial({ color: 0xFDD835 });
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.y = 0.75;
                break;
                
            case 'wheat-sentinel':
                geometry = new THREE.CylinderGeometry(0.12, 0.05, 1.8, 8);
                material = new THREE.MeshLambertMaterial({ color: 0x9CCC65 }); // Slightly different color
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.y = 0.9;
                break;
                
            case 'apple':
            case 'pear':
                // Create fruit tree
                // Tree trunk
                const fruitTrunkGeometry = new THREE.CylinderGeometry(0.3, 0.4, 2, 8);
                const fruitTrunkMaterial = new THREE.MeshLambertMaterial({ color: 0x8D6E63 });
                const fruitTrunk = new THREE.Mesh(fruitTrunkGeometry, fruitTrunkMaterial);
                fruitTrunk.position.y = 1;
                
                // Tree foliage
                const fruitFoliageGeometry = new THREE.SphereGeometry(1.2, 8, 8);
                const fruitFoliageMaterial = new THREE.MeshLambertMaterial({ 
                    color: modelType === 'apple' ? 0x2E7D32 : 0x388E3C 
                });
                const fruitFoliage = new THREE.Mesh(fruitFoliageGeometry, fruitFoliageMaterial);
                fruitFoliage.position.y = 2.5;
                
                // Add fruit
                const fruitColor = modelType === 'apple' ? 0xE53935 : 0xFFB300;
                const fruitCount = 3 + Math.floor(Math.random() * 5);
                
                mesh = new THREE.Group();
                mesh.add(fruitTrunk);
                mesh.add(fruitFoliage);
                
                // Add random fruits
                for (let i = 0; i < fruitCount; i++) {
                    const fruitGeometry = new THREE.SphereGeometry(0.15, 8, 8);
                    const fruitMaterial = new THREE.MeshLambertMaterial({ color: fruitColor });
                    const fruit = new THREE.Mesh(fruitGeometry, fruitMaterial);
                    
                    // Random position within foliage
                    const theta = Math.random() * Math.PI * 2;
                    const phi = Math.random() * Math.PI;
                    const radius = 0.8 + Math.random() * 0.3;
                    
                    fruit.position.x = radius * Math.sin(phi) * Math.cos(theta);
                    fruit.position.y = 2.5 + radius * Math.cos(phi);
                    fruit.position.z = radius * Math.sin(phi) * Math.sin(theta);
                    
                    mesh.add(fruit);
                }
                break;
                
            case 'tree':
                // Tree trunk
                const trunkGeometry = new THREE.CylinderGeometry(0.3, 0.4, 2, 8);
                const trunkMaterial = new THREE.MeshLambertMaterial({ color: 0x8D6E63 });
                const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
                trunk.position.y = 1;
                
                // Tree foliage
                const foliageGeometry = new THREE.ConeGeometry(1.5, 3, 8);
                const foliageMaterial = new THREE.MeshLambertMaterial({ color: 0x2E7D32 });
                const foliage = new THREE.Mesh(foliageGeometry, foliageMaterial);
                foliage.position.y = 3;
                
                // Group trunk and foliage
                mesh = new THREE.Group();
                mesh.add(trunk);
                mesh.add(foliage);
                break;
                
            case 'fungal':
                geometry = new THREE.SphereGeometry(0.3, 16, 16);
                material = new THREE.MeshBasicMaterial({ color: 0x9C27B0, opacity: 0.8, transparent: true });
                mesh = new THREE.Mesh(geometry, material);
                break;
                
            case 'bacterial':
                geometry = new THREE.BoxGeometry(0.4, 0.4, 0.4);
                material = new THREE.MeshBasicMaterial({ color: 0xF44336, opacity: 0.8, transparent: true });
                mesh = new THREE.Mesh(geometry, material);
                break;
                
            case 'viral':
                geometry = new THREE.TetrahedronGeometry(0.3);
                material = new THREE.MeshBasicMaterial({ color: 0xFF9800, opacity: 0.8, transparent: true });
                mesh = new THREE.Mesh(geometry, material);
                break;
                
            case 'pest':
                geometry = new THREE.OctahedronGeometry(0.3);
                material = new THREE.MeshBasicMaterial({ color: 0x4CAF50, opacity: 0.8, transparent: true });
                mesh = new THREE.Mesh(geometry, material);
                break;
                
            default:
                console.error(`Unknown model type: ${modelType}`);
                return;
        }
        
        // Store the fallback model
        loadedModels.set(modelType, mesh);
    };
    
    if (specificModel === 'all' || specificModel === null) {
        createModels('corn');
        createModels('corn-standard');
        createModels('corn-bt');
        createModels('wheat');
        createModels('wheat-standard');
        createModels('wheat-sentinel');
        createModels('tree');
        createModels('apple');
        createModels('pear');
        createModels('fungal');
        createModels('bacterial');
        createModels('viral');
        createModels('pest');
    } else {
        createModels(specificModel);
    }
}

// Render field based on field data
async function renderField(field) {
    if (!field) return;
    
    // Create ground plane with direct cropimage.jpg texture
    const planeGeometry = new THREE.PlaneGeometry(field.width, field.height);
    
    // Directly load cropimage.jpg texture
    const textureLoader = new THREE.TextureLoader();
    const satelliteTexture = await new Promise((resolve) => {
        textureLoader.load(
            'cropimage.jpg',  // Direct reference to the file
            (texture) => {
                texture.wrapS = THREE.RepeatWrapping;
                texture.wrapT = THREE.RepeatWrapping;
                texture.repeat.set(1, 1);
                resolve(texture);
            },
            undefined,
            (error) => {
                console.error('Error loading cropimage.jpg:', error);
                // Create a fallback texture on error
                const canvas = document.createElement('canvas');
                canvas.width = 1024;
                canvas.height = 1024;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#689F38';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                resolve(new THREE.CanvasTexture(canvas));
            }
        );
    });
    
    const planeMaterial = new THREE.MeshStandardMaterial({
        map: satelliteTexture,
        side: THREE.DoubleSide,
        roughness: 0.8,
        metalness: 0.2
    });
    
    const plane = new THREE.Mesh(planeGeometry, planeMaterial);
    plane.rotation.x = -Math.PI / 2;
    plane.position.y = 0;
    plane.receiveShadow = true;
    scene.add(plane);
    
    // Render crops based on field data
    field.crops.forEach(crop => {
        const cropModel = loadedModels.get(crop.type).clone();
        cropModel.position.set(crop.x, 0, crop.z);
        cropModel.scale.set(crop.scale, crop.scale, crop.scale);
        cropModel.rotation.y = Math.random() * Math.PI * 2; // Random rotation for variety
        
        // Add shadows
        cropModel.traverse(child => {
            if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });
        
        scene.add(cropModel);
    });
    
    // Render field boundaries or fences
    renderFieldBoundaries(field);
    
    // Update camera position based on field size
    const fieldDiagonal = Math.sqrt(field.width * field.width + field.height * field.height);
    camera.position.set(0, fieldDiagonal * 0.5, fieldDiagonal * 0.5);
    controls.target.set(0, 0, 0);
    controls.update();
    
    // Render threats
    updateThreats(field.threats, appState);
    
    // Render sensors and drones
    renderSensors(field);
    renderDrones(field);
}

// Render field sensors
function renderSensors(field) {
    if (!field.sensors || field.sensors.length === 0) return;
    
    const sensorsGroup = new THREE.Group();
    sensorsGroup.name = 'sensors';
    
    field.sensors.forEach(sensor => {
        const sensorMesh = createSensorMesh(sensor);
        sensorMesh.position.set(sensor.x, 0, sensor.z);
        sensorMesh.userData = { 
            isSensor: true,
            ...sensor 
        };
        sensorsGroup.add(sensorMesh);
    });
    
    scene.add(sensorsGroup);
}

// Create a visual representation of a sensor based on its type
function createSensorMesh(sensor) {
    // Make sensors 5x larger by increasing dimensions
    const sensorScaleFactor = 5.0;
    const { type, height, color, shape, radius } = sensor;
    const scaledHeight = height * sensorScaleFactor;
    const scaledRadius = radius * sensorScaleFactor;
    
    const sensorGroup = new THREE.Group();
    let mainGeometry, mainMaterial, mainMesh;
    
    // Create the main sensor body based on shape
    switch(shape) {
        case 'cylinder':
            mainGeometry = new THREE.CylinderGeometry(scaledRadius, scaledRadius, scaledHeight, 8);
            break;
        case 'pole':
            mainGeometry = new THREE.CylinderGeometry(scaledRadius/3, scaledRadius, scaledHeight, 8);
            break;
        case 'sphere':
            mainGeometry = new THREE.SphereGeometry(scaledRadius, 16, 16);
            break;
        case 'cone':
            mainGeometry = new THREE.ConeGeometry(scaledRadius, scaledHeight, 8);
            break;
        case 'box':
            mainGeometry = new THREE.BoxGeometry(scaledRadius*2, scaledHeight, scaledRadius*2);
            break;
        case 'pyramid':
            mainGeometry = new THREE.ConeGeometry(scaledRadius, scaledHeight, 4);
            break;
        default:
            mainGeometry = new THREE.CylinderGeometry(scaledRadius, scaledRadius, scaledHeight, 8);
    }
    
    // Create material with sensor color
    mainMaterial = new THREE.MeshStandardMaterial({ 
        color: color,
        metalness: 0.5,
        roughness: 0.2
    });
    
    mainMesh = new THREE.Mesh(mainGeometry, mainMaterial);
    mainMesh.castShadow = true;
    mainMesh.position.y = scaledHeight / 2;
    sensorGroup.add(mainMesh);
    
    // Add indicator light
    const lightGeometry = new THREE.SphereGeometry(scaledRadius/3, 8, 8);
    const lightMaterial = new THREE.MeshBasicMaterial({ 
        color: sensor.status === 'active' ? 0x00FF00 : 0xFF0000,
        emissive: sensor.status === 'active' ? 0x00FF00 : 0xFF0000,
        emissiveIntensity: 0.5
    });
    const light = new THREE.Mesh(lightGeometry, lightMaterial);
    light.position.y = scaledHeight + scaledRadius/3;
    sensorGroup.add(light);
    
    // Add small base
    const baseGeometry = new THREE.CylinderGeometry(scaledRadius*1.2, scaledRadius*1.5, 0.2*sensorScaleFactor, 8);
    const baseMaterial = new THREE.MeshStandardMaterial({ color: 0x333333 });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.y = 0.1*sensorScaleFactor;
    sensorGroup.add(base);
    
    return sensorGroup;
}

// Render drones
function renderDrones(field) {
    if (!field.drones || field.drones.length === 0) return;
    
    const dronesGroup = new THREE.Group();
    dronesGroup.name = 'drones';
    
    field.drones.forEach(drone => {
        const droneMesh = createDroneMesh(drone);
        droneMesh.position.set(
            drone.position.x, 
            drone.position.y, 
            drone.position.z
        );
        droneMesh.userData = { 
            isDrone: true,
            ...drone 
        };
        dronesGroup.add(droneMesh);
        
        // Initialize drone animations
        animateDrone(droneMesh, drone);
    });
    
    scene.add(dronesGroup);
}

// Create a visual representation of a drone
function createDroneMesh(drone) {
    const droneGroup = new THREE.Group();
    
    // Drone body
    const bodyGeometry = new THREE.BoxGeometry(1.5, 0.4, 1.5);
    const bodyMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x222222,
        metalness: 0.7,
        roughness: 0.2
    });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    droneGroup.add(body);
    
    // Drone rotors (4 corners)
    const rotorPositions = [
        { x: 0.8, z: 0.8 },
        { x: 0.8, z: -0.8 },
        { x: -0.8, z: 0.8 },
        { x: -0.8, z: -0.8 }
    ];
    
    rotorPositions.forEach((pos, i) => {
        // Rotor mount
        const mountGeometry = new THREE.CylinderGeometry(0.1, 0.1, 0.2, 8);
        const mountMaterial = new THREE.MeshStandardMaterial({ color: 0x444444 });
        const mount = new THREE.Mesh(mountGeometry, mountMaterial);
        mount.position.set(pos.x, 0.2, pos.z);
        droneGroup.add(mount);
        
        // Rotor blade
        const rotorGeometry = new THREE.BoxGeometry(0.8, 0.05, 0.1);
        const rotorMaterial = new THREE.MeshStandardMaterial({ color: 0x888888 });
        const rotor = new THREE.Mesh(rotorGeometry, rotorMaterial);
        rotor.position.set(pos.x, 0.3, pos.z);
        rotor.name = `rotor-${i}`;
        droneGroup.add(rotor);
    });
    
    // Add sensor payload based on drone type
    let payloadGeometry, payloadMaterial;
    
    switch(drone.type) {
        case 'scanner':
            payloadGeometry = new THREE.SphereGeometry(0.4, 16, 16);
            payloadMaterial = new THREE.MeshStandardMaterial({ 
                color: 0x1E88E5,
                metalness: 0.5,
                roughness: 0.2
            });
            break;
        case 'sprayer':
            payloadGeometry = new THREE.CylinderGeometry(0.3, 0.1, 0.6, 8);
            payloadMaterial = new THREE.MeshStandardMaterial({ 
                color: 0x43A047,
                metalness: 0.3,
                roughness: 0.4
            });
            break;
        case 'sampler':
            payloadGeometry = new THREE.BoxGeometry(0.5, 0.4, 0.5);
            payloadMaterial = new THREE.MeshStandardMaterial({ 
                color: 0xFB8C00,
                metalness: 0.4,
                roughness: 0.3
            });
            break;
        default:
            payloadGeometry = new THREE.BoxGeometry(0.5, 0.3, 0.5);
            payloadMaterial = new THREE.MeshStandardMaterial({ color: 0xE0E0E0 });
    }
    
    const payload = new THREE.Mesh(payloadGeometry, payloadMaterial);
    payload.position.y = -0.4;
    droneGroup.add(payload);
    
    // Add status light
    const lightGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const lightMaterial = new THREE.MeshBasicMaterial({ 
        color: drone.status === 'active' ? 0x00FF00 : 0xFF9800,
        emissive: drone.status === 'active' ? 0x00FF00 : 0xFF9800,
        emissiveIntensity: 1
    });
    const light = new THREE.Mesh(lightGeometry, lightMaterial);
    light.position.set(0, 0, -0.8);
    droneGroup.add(light);
    
    return droneGroup;
}

// Animate drone movement along its path
function animateDrone(droneMesh, drone) {
    if (!drone.path || drone.path.length < 2) return;
    
    const animate = () => {
        if (!droneMesh || !droneMesh.parent) return;
        
        // Animate rotors
        droneMesh.children.forEach(child => {
            if (child.name && child.name.startsWith('rotor')) {
                child.rotation.y += 0.5; // Spin rotors
            }
        });
        
        // Move drone along path
        const currentPoint = drone.path[drone.currentPointIndex];
        const targetPoint = drone.path[(drone.currentPointIndex + 1) % drone.path.length];
        
        // Calculate direction and distance
        const direction = new THREE.Vector3(
            targetPoint.x - droneMesh.position.x,
            targetPoint.y - droneMesh.position.y,
            targetPoint.z - droneMesh.position.z
        );
        
        const distance = direction.length();
        
        if (distance < 0.5) {
            // Reached target point, move to next point
            drone.currentPointIndex = (drone.currentPointIndex + 1) % drone.path.length;
        } else {
            // Move towards target
            direction.normalize();
            droneMesh.position.x += direction.x * drone.speed;
            droneMesh.position.y += direction.y * drone.speed;
            droneMesh.position.z += direction.z * drone.speed;
            
            // Rotate to face direction
            droneMesh.lookAt(
                droneMesh.position.x + direction.x,
                droneMesh.position.y + direction.y,
                droneMesh.position.z + direction.z
            );
        }
        
        // Small hovering motion
        droneMesh.position.y += Math.sin(Date.now() * 0.003) * 0.02;
        
        requestAnimationFrame(animate);
    };
    
    animate();
}

// Render field boundaries
function renderFieldBoundaries(field) {
    const width = field.width;
    const height = field.height;
    
    // Create fence posts and rails
    const postsGroup = new THREE.Group();
    
    // Material for wooden fence
    const woodMaterial = new THREE.MeshLambertMaterial({ color: 0x8D6E63 });
    
    // Create fence along perimeter
    const postSpacing = 5;
    const postHeight = 1.5;
    const postRadius = 0.2;
    const railHeight = 1.2;
    const railRadius = 0.1;
    
    // Function to create a post
    const createPost = (x, z) => {
        const postGeometry = new THREE.CylinderGeometry(postRadius, postRadius, postHeight, 8);
        const post = new THREE.Mesh(postGeometry, woodMaterial);
        post.position.set(x, postHeight / 2, z);
        post.castShadow = true;
        return post;
    };
    
    // Function to create a rail between two points
    const createRail = (x1, z1, x2, z2) => {
        const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(z2 - z1, 2));
        const railGeometry = new THREE.CylinderGeometry(railRadius, railRadius, length, 8);
        const rail = new THREE.Mesh(railGeometry, woodMaterial);
        
        // Position at midpoint
        rail.position.set((x1 + x2) / 2, railHeight, (z1 + z2) / 2);
        
        // Rotate to point from p1 to p2
        rail.rotation.y = Math.atan2(x2 - x1, z2 - z1);
        rail.rotation.x = Math.PI / 2;
        
        rail.castShadow = true;
        return rail;
    };
    
    // Create fence along x-axis (bottom and top)
    const halfWidth = width / 2;
    const halfHeight = height / 2;
    
    for (let x = -halfWidth; x <= halfWidth; x += postSpacing) {
        // Bottom edge
        postsGroup.add(createPost(x, -halfHeight));
        if (x < halfWidth) {
            postsGroup.add(createRail(x, -halfHeight, x + postSpacing, -halfHeight));
        }
        
        // Top edge
        postsGroup.add(createPost(x, halfHeight));
        if (x < halfWidth) {
            postsGroup.add(createRail(x, halfHeight, x + postSpacing, halfHeight));
        }
    }
    
    // Create fence along z-axis (left and right)
    for (let z = -halfHeight + postSpacing; z < halfHeight; z += postSpacing) {
        // Left edge
        postsGroup.add(createPost(-halfWidth, z));
        postsGroup.add(createRail(-halfWidth, z, -halfWidth, z + postSpacing));
        
        // Right edge
        postsGroup.add(createPost(halfWidth, z));
        postsGroup.add(createRail(halfWidth, z, halfWidth, z + postSpacing));
    }
    
    scene.add(postsGroup);
}

// Update visibility of threats based on current filters
function updateThreatVisibility() {
    updateThreats(currentField.threats, appState);
}

// Handle window resize
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Handle mouse move for hover effects
function onMouseMove(event) {
    // Calculate mouse position in normalized device coordinates
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    
    // Raycast to find intersecting objects
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);
    
    // Reset hover status
    if (appState.hoverObject) {
        appState.hoverObject.traverse(child => {
            if (child.isMesh && child._originalColor) {
                child.material.color.copy(child._originalColor);
                delete child._originalColor;
            }
        });
    }
    
    // Remove any existing tooltip
    removeTooltip();
    
    // Find the first intersected object with userdata
    for (let i = 0; i < intersects.length; i++) {
        const object = findParentWithUserData(intersects[i].object);
        
        if (object && object !== appState.selectedObject) {
            // Store original color for resetting later
            object.traverse(child => {
                if (child.isMesh && !child._originalColor) {
                    child._originalColor = child.material.color.clone();
                    child.material.color.lerp(new THREE.Color(0xFFFFFF), 0.3);
                }
            });
            
            // Set as hover object
            appState.hoverObject = object;
            
            // Show tooltip if object has userData
            if (object.userData && object.userData.type) {
                showTooltip(object, event);
            }
            
            break;
        }
    }
}

// Handle mouse click for selection
function onMouseClick(event) {
    // Reset previous selection visual
    if (appState.selectedObject) {
        appState.selectedObject.traverse(child => {
            if (child.isMesh && child._selectionColor) {
                child.material.color.copy(child._selectionColor);
                delete child._selectionColor;
            }
        });
    }
    
    // Raycast to find intersecting objects
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);
    
    // Find the first intersected object with userdata
    for (let i = 0; i < intersects.length; i++) {
        const object = findParentWithUserData(intersects[i].object);
        
        if (object) {
            // Store selection color for resetting later
            object.traverse(child => {
                if (child.isMesh) {
                    child._selectionColor = child.material.color.clone();
                    child.material.color.lerp(new THREE.Color(0xFFD700), 0.5); // Gold highlight
                }
            });
            
            // Set as selected object
            appState.selectedObject = object;
            
            // Show details panel if it's a threat
            if (object.userData && object.userData.isThreat) {
                showThreatDetails(object.userData);
            }
            
            break;
        }
    }
    
    // If no object was clicked, hide the threat info panel
    if (intersects.length === 0 || !appState.selectedObject) {
        document.querySelector('.threat-info-panel').style.display = 'none';
    }
}

// Find parent object with userData
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

// Show tooltip
function showTooltip(object, event) {
    removeTooltip(); // Remove any existing tooltip
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    
    // Determine content based on object type
    if (object.userData.isThreat) {
        const threat = object.userData;
        tooltip.innerHTML = `
            <strong>${threat.name}</strong><br>
            Type: ${threat.type}<br>
            Severity: ${threat.severity}
        `;
    } else {
        tooltip.innerHTML = `<strong>${object.userData.type}</strong>`;
    }
    
    // Position tooltip at mouse
    tooltip.style.left = `${event.clientX}px`;
    tooltip.style.top = `${event.clientY}px`;
    
    // Add to DOM
    document.body.appendChild(tooltip);
}

// Remove tooltip
function removeTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Show threat details panel
function showThreatDetails(threat) {
    const panel = document.querySelector('.threat-info-panel');
    const content = panel.querySelector('.panel-content');
    
    // Create content for the threat details
    content.innerHTML = `
        <div class="threat-details ${threat.type.toLowerCase()}">
            <div class="threat-title">
                ${threat.name}
                <span class="threat-severity ${threat.severity.toLowerCase()}">${threat.severity}</span>
            </div>
            <p><strong>Type:</strong> ${threat.type}</p>
            <p><strong>Location:</strong> ${threat.location.x.toFixed(1)}, ${threat.location.z.toFixed(1)}</p>
            <p><strong>Detected:</strong> ${threat.detectedDate}</p>
            <p><strong>Affected Area:</strong> ${threat.affectedArea} sq m</p>
            <p>${threat.description}</p>
            <div class="threat-actions">
                <button class="btn-primary">Treatment Options</button>
                <button class="btn-secondary">Mark Resolved</button>
            </div>
        </div>
    `;
    
    // Show the panel
    panel.style.display = 'block';
}

// Handle controls change
function onControlsChanged(key, value) {
    appState[key] = value;
    
    // Handle specific state changes
    switch (key) {
        case 'viewMode':
            updateCameraPosition(value);
            break;
        case 'selectedFieldId':
            loadNewField(value);
            break;
        case 'selectedThreats':
        case 'activeThreatFilter':
        case 'timeRange':
            updateThreatVisibility();
            break;
    }
}

// Update camera position based on view mode
function updateCameraPosition(viewMode) {
    // If no field is loaded, do nothing
    if (!currentField) return;
    
    const fieldWidth = currentField.width;
    const fieldHeight = currentField.height;
    const diagonal = Math.sqrt(fieldWidth * fieldWidth + fieldHeight * fieldHeight);
    
    // Toggle drone FPV view based on view mode
    const droneFpvView = document.querySelector('.drone-fpv-view');
    if (droneFpvView) {
        droneFpvView.style.display = viewMode === 'drone' ? 'flex' : 'none';
        
        // Update drone metrics if in drone view
        if (viewMode === 'drone') {
            updateDroneMetrics();
        }
    }
    
    // Smooth transition to new position with GSAP
    switch (viewMode) {
        case 'overhead':
            gsap.to(camera.position, {
                x: 0, 
                y: diagonal * 0.7, 
                z: 0,
                duration: 1.5,
                ease: 'power2.inOut',
                onUpdate: () => controls.update()
            });
            gsap.to(controls.target, {
                x: 0, y: 0, z: 0,
                duration: 1.5,
                ease: 'power2.inOut'
            });
            break;
            
        case 'firstPerson':
            // Position at edge of field
            gsap.to(camera.position, {
                x: -fieldWidth * 0.45, 
                y: 1.7, 
                z: -fieldHeight * 0.45,
                duration: 1.5,
                ease: 'power2.inOut',
                onUpdate: () => controls.update()
            });
            gsap.to(controls.target, {
                x: 0, y: 1, z: 0,
                duration: 1.5,
                ease: 'power2.inOut'
            });
            break;
            
        case 'drone':
            // Put camera in drone position above field
            gsap.to(camera.position, {
                x: fieldWidth * 0.25, 
                y: diagonal * 0.3, 
                z: fieldHeight * 0.25,
                duration: 1.5,
                ease: 'power2.inOut',
                onUpdate: () => {
                    controls.update();
                    if (viewMode === 'drone') {
                        updateDroneMetrics(); // Update metrics during animation
                    }
                }
            });
            gsap.to(controls.target, {
                x: 0, y: 0, z: 0,
                duration: 1.5,
                ease: 'power2.inOut'
            });
            break;
    }
    
    // Update control constraints based on view mode
    if (viewMode === 'firstPerson') {
        controls.maxPolarAngle = Math.PI - 0.1; // Allow looking up/down
        controls.minDistance = 0.1;
    } else {
        controls.maxPolarAngle = Math.PI / 2 - 0.1; // Restrict to not go below ground
        controls.minDistance = 5;
    }
}

// Update drone metrics for the FPV display
function updateDroneMetrics() {
    // Get drone altitude (camera y position)
    const altitude = Math.round(camera.position.y);
    const altitudeElement = document.getElementById('drone-altitude');
    if (altitudeElement) {
        altitudeElement.textContent = altitude;
    }
    
    // Calculate drone speed (simulated based on movement or random for demo)
    const speed = Math.floor(Math.random() * 5) + 10; // Random speed between 10-15 m/s for demo
    const speedElement = document.getElementById('drone-speed');
    if (speedElement) {
        speedElement.textContent = speed;
    }
}

// Load a new field
async function loadNewField(fieldId) {
    showLoadingScreen(true);
    
    // Clear the current scene of field elements
    clearFieldFromScene();
    
    // Load new field data
    currentField = await loadFieldData(fieldId);
    
    // Render the new field
    renderField(currentField);
    
    // Update the camera based on current view mode
    updateCameraPosition(appState.viewMode);
    
    showLoadingScreen(false);
}

// Clear field-related objects from the scene
function clearFieldFromScene() {
    // Remove objects from scene
    const objectsToRemove = [];
    
    scene.traverse(object => {
        // Keep lights and helpers, remove everything else
        if (
            object !== scene && 
            !(object instanceof THREE.AmbientLight) && 
            !(object instanceof THREE.DirectionalLight) && 
            !(object instanceof THREE.HemisphereLight) && 
            !(object instanceof THREE.AxesHelper) && 
            !(object instanceof THREE.GridHelper)
        ) {
            objectsToRemove.push(object);
        }
    });
    
    // Also explicitly find and remove sensor and drone groups
    scene.children.forEach(child => {
        if (child.name === 'sensors' || child.name === 'drones') {
            objectsToRemove.push(child);
        }
    });
    
    // Remove collected objects
    objectsToRemove.forEach(object => {
        scene.remove(object);
    });
}

// Show/hide loading screen
function showLoadingScreen(show) {
    const loadingScreen = document.getElementById('loading-screen');
    appState.isLoading = show;
    
    if (show) {
        loadingScreen.style.display = 'flex';
    } else {
        gsap.to(loadingScreen, {
            opacity: 0,
            duration: 0.5,
            onComplete: () => {
                loadingScreen.style.display = 'none';
                loadingScreen.style.opacity = 1;
            }
        });
    }
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    
    // Update controls
    controls.update();
    
    // Update any animation mixers
    const delta = clock.getDelta();
    mixers.forEach(mixer => mixer.update(delta));
    
    // Render the scene
    renderer.render(scene, camera);
}

// Initialize the application once window loads
window.addEventListener('load', init);

// Export necessary functions and objects
export {
    scene,
    camera,
    appState,
    updateThreatVisibility
};
