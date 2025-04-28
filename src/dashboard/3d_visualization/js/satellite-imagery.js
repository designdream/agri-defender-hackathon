// satellite-imagery.js - Handles satellite and drone imagery integration

// Satellite imagery sources (using real agricultural satellite imagery APIs)
const satelliteImageSources = {
    // Sentinel-2 satellite imagery (real open source satellite data)
    sentinel: {
        field1: 'https://services.sentinel-hub.com/ogc/wms/your-instance-id?REQUEST=GetMap&CRS=EPSG:4326&BBOX=42.6,-71.8,42.7,-71.7&WIDTH=512&HEIGHT=512&LAYERS=TRUE-COLOR&FORMAT=image/jpeg&TIME=2024-04-01/2025-04-30',
        field2: 'https://services.sentinel-hub.com/ogc/wms/your-instance-id?REQUEST=GetMap&CRS=EPSG:4326&BBOX=42.5,-71.9,42.6,-71.8&WIDTH=512&HEIGHT=512&LAYERS=TRUE-COLOR&FORMAT=image/jpeg&TIME=2024-04-01/2025-04-30',
        field3: 'https://services.sentinel-hub.com/ogc/wms/your-instance-id?REQUEST=GetMap&CRS=EPSG:4326&BBOX=42.4,-71.8,42.5,-71.7&WIDTH=512&HEIGHT=512&LAYERS=TRUE-COLOR&FORMAT=image/jpeg&TIME=2024-04-01/2025-04-30'
    },
    // Drone imagery (high-resolution field surveys)
    drone: {
        field1: 'https://example.com/api/drone-imagery/field1/latest',
        field2: 'https://example.com/api/drone-imagery/field2/latest',
        field3: 'https://example.com/api/drone-imagery/field3/latest'
    },
    // Fallback imagery (static terrain maps for demonstration)
    fallback: {
        field1: '../cropimage.jpg', // Local crop image
        field2: '../cropimage.jpg', // Local crop image
        field3: '../cropimage.jpg'  // Local crop image
    }
};

// Default satellite imagery options to use when actual API keys aren't available
const defaultSatelliteImages = {
    field1: '../cropimage.jpg',
    field2: '../cropimage.jpg',
    field3: '../cropimage.jpg'
};

// Normalized difference vegetation index (NDVI) imagery for vegetation health analysis
const ndviImageSources = {
    field1: '../cropimage.jpg', // Using local crop image for NDVI as well
    field2: '../cropimage.jpg', // Using local crop image for NDVI as well
    field3: '../cropimage.jpg'  // Using local crop image for NDVI as well
};

// Load satellite imagery texture for Three.js
async function loadSatelliteTexture(fieldId, imageType = 'fallback') {
    return new Promise((resolve, reject) => {
        try {
            // Image source determination with fallbacks
            let imageSource;
            
            // Try to get source from configured sources
            if (satelliteImageSources[imageType] && satelliteImageSources[imageType][fieldId]) {
                imageSource = satelliteImageSources[imageType][fieldId];
            } 
            // Fallback to default static images if API sources not available
            else if (satelliteImageSources.fallback[fieldId]) {
                console.log('Using fallback satellite imagery for', fieldId);
                imageSource = satelliteImageSources.fallback[fieldId];
            } 
            // Final fallback - use a color for the field
            else {
                console.warn('No satellite image available for', fieldId);
                // Create a blank green texture as final fallback
                const canvas = document.createElement('canvas');
                canvas.width = 1024;
                canvas.height = 1024;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#4CAF50';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw some field patterns
                ctx.strokeStyle = '#3E8E41';
                ctx.lineWidth = 2;
                for (let i = 0; i < canvas.width; i += 50) {
                    ctx.beginPath();
                    ctx.moveTo(i, 0);
                    ctx.lineTo(i, canvas.height);
                    ctx.stroke();
                    
                    ctx.beginPath();
                    ctx.moveTo(0, i);
                    ctx.lineTo(canvas.width, i);
                    ctx.stroke();
                }
                
                const texture = new THREE.CanvasTexture(canvas);
                texture.wrapS = THREE.RepeatWrapping;
                texture.wrapT = THREE.RepeatWrapping;
                texture.repeat.set(1, 1);
                resolve(texture);
                return;
            }
            
            // Load texture with THREE.TextureLoader
            const textureLoader = new THREE.TextureLoader();
            textureLoader.crossOrigin = 'anonymous';
            // Encode URI to handle spaces in filenames
            const encodedImageSource = imageSource.includes(' ') ? encodeURI(imageSource) : imageSource;
            textureLoader.load(
                encodedImageSource,
                (texture) => {
                    // Configure texture for proper field mapping
                    texture.wrapS = THREE.RepeatWrapping;
                    texture.wrapT = THREE.RepeatWrapping;
                    texture.repeat.set(1, 1);
                    resolve(texture);
                },
                (xhr) => {
                    console.log(`Satellite image ${fieldId} ${Math.round(xhr.loaded / xhr.total * 100)}% loaded`);
                },
                (error) => {
                    console.error('Error loading satellite texture:', error);
                    // Create a fallback texture on error
                    const canvas = document.createElement('canvas');
                    canvas.width = 1024;
                    canvas.height = 1024;
                    const ctx = canvas.getContext('2d');
                    ctx.fillStyle = '#689F38';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    const texture = new THREE.CanvasTexture(canvas);
                    resolve(texture);
                }
            );
        } catch (error) {
            console.error('Satellite image loading error:', error);
            reject(error);
        }
    });
}

// Get NDVI texture for analysis view
async function loadNDVITexture(fieldId) {
    return new Promise((resolve, reject) => {
        if (!ndviImageSources[fieldId]) {
            console.warn('No NDVI image available for', fieldId);
            resolve(null);
            return;
        }

        const textureLoader = new THREE.TextureLoader();
        textureLoader.crossOrigin = 'anonymous';
        textureLoader.load(
            ndviImageSources[fieldId],
            (texture) => {
                texture.wrapS = THREE.RepeatWrapping;
                texture.wrapT = THREE.RepeatWrapping;
                resolve(texture);
            },
            undefined,
            (error) => {
                console.error('Error loading NDVI texture:', error);
                resolve(null);
            }
        );
    });
}

// Create directories for local satellite imagery assets
async function createLocalSatelliteImageDirectories() {
    // This would normally create local directories for satellite images
    // In a web context, we'll just log that we're ready for images
    console.log('Ready for local satellite imagery assets in ./assets/');
    return true;
}

// Export functions and data
export { 
    loadSatelliteTexture, 
    loadNDVITexture,
    createLocalSatelliteImageDirectories,
    satelliteImageSources,
    ndviImageSources
};
