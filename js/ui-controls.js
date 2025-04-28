// ui-controls.js - Handles user interface controls and interactions

// Store references to UI elements
const uiElements = {};

// Store callback function for control changes
let controlChangeCallback = null;

// Initialize UI controls
function initializeControls(appState, callback) {
    // Store the callback
    controlChangeCallback = callback;
    
    // Cache UI element references
    cacheUIElements();
    
    // Set up initial control values from app state
    initializeControlValues(appState);
    
    // Set up event listeners
    setupEventListeners(appState);
    
    // Set up field selector
    populateFieldSelector();
    
    // Update date and weather info
    updateDateTime();
    setInterval(updateDateTime, 60000); // Update every minute
    
    // Update statistics display
    updateStatsDisplay(appState);
}

// Cache references to UI elements
function cacheUIElements() {
    // Panel controls
    uiElements.controlsPanel = document.querySelector('.controls-panel');
    uiElements.controlsToggle = document.querySelector('.panel-header .btn-icon');
    
    // View mode controls
    uiElements.viewModeButtons = document.querySelectorAll('.view-mode-controls .control-btn');
    
    // Threat filters
    uiElements.threatCheckboxes = {
        fungal: document.querySelector('input[name="filter-fungal"]'),
        bacterial: document.querySelector('input[name="filter-bacterial"]'),
        viral: document.querySelector('input[name="filter-viral"]'),
        pest: document.querySelector('input[name="filter-pest"]')
    };
    
    // Severity filter
    uiElements.severityButtons = document.querySelectorAll('.severity-controls .control-btn');
    
    // Time range slider
    uiElements.timeSlider = document.querySelector('#time-range');
    uiElements.timeLabel = document.querySelector('#time-value');
    
    // Field selector
    uiElements.fieldSelector = document.querySelector('#field-selector');
    
    // Stats display
    uiElements.statValues = {
        threats: document.querySelector('#stat-threats'),
        affected: document.querySelector('#stat-affected'),
        health: document.querySelector('#stat-health')
    };
    
    // Date and weather display
    uiElements.dateTime = document.querySelector('.date-time');
    uiElements.weatherInfo = document.querySelector('.weather-info');
    
    // Threat info panel
    uiElements.threatInfoPanel = document.querySelector('.threat-info-panel');
    uiElements.threatInfoClose = document.querySelector('.threat-info-panel .btn-icon');
}

// Initialize control values based on app state
function initializeControlValues(appState) {
    // Set view mode
    uiElements.viewModeButtons.forEach(button => {
        if (button.dataset.mode === appState.viewMode) {
            button.classList.add('active');
        }
    });
    
    // Set threat type checkboxes
    for (const [type, checked] of Object.entries(appState.selectedThreats)) {
        if (uiElements.threatCheckboxes[type]) {
            uiElements.threatCheckboxes[type].checked = checked;
        }
    }
    
    // Set severity filter
    uiElements.severityButtons.forEach(button => {
        if (button.dataset.severity === appState.activeThreatFilter) {
            button.classList.add('active');
        }
    });
    
    // Set time range
    if (uiElements.timeSlider) {
        uiElements.timeSlider.value = appState.timeRange;
        uiElements.timeLabel.textContent = `${appState.timeRange} days`;
    }
}

// Set up event listeners for controls
function setupEventListeners(appState) {
    // Toggle control panel
    if (uiElements.controlsToggle) {
        uiElements.controlsToggle.addEventListener('click', () => {
            uiElements.controlsPanel.classList.toggle('collapsed');
        });
    }
    
    // View mode buttons
    uiElements.viewModeButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            uiElements.viewModeButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Update app state
            const mode = button.dataset.mode;
            appState.viewMode = mode;
            
            // Notify callback
            if (controlChangeCallback) {
                controlChangeCallback('viewMode', mode);
            }
        });
    });
    
    // Threat checkboxes
    for (const [type, checkbox] of Object.entries(uiElements.threatCheckboxes)) {
        if (checkbox) {
            checkbox.addEventListener('change', () => {
                // Update app state
                appState.selectedThreats[type] = checkbox.checked;
                
                // Notify callback
                if (controlChangeCallback) {
                    controlChangeCallback('selectedThreats', appState.selectedThreats);
                }
                
                // Update stats
                updateStatsDisplay(appState);
            });
        }
    }
    
    // Severity buttons
    uiElements.severityButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            uiElements.severityButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Update app state
            const severity = button.dataset.severity;
            appState.activeThreatFilter = severity;
            
            // Notify callback
            if (controlChangeCallback) {
                controlChangeCallback('activeThreatFilter', severity);
            }
            
            // Update stats
            updateStatsDisplay(appState);
        });
    });
    
    // Time range slider
    if (uiElements.timeSlider) {
        uiElements.timeSlider.addEventListener('input', () => {
            const value = parseInt(uiElements.timeSlider.value);
            
            // Update label
            uiElements.timeLabel.textContent = `${value} days`;
            
            // Notify callback (but don't update state yet to avoid too many updates)
        });
        
        uiElements.timeSlider.addEventListener('change', () => {
            const value = parseInt(uiElements.timeSlider.value);
            
            // Update app state
            appState.timeRange = value;
            
            // Notify callback
            if (controlChangeCallback) {
                controlChangeCallback('timeRange', value);
            }
            
            // Update stats
            updateStatsDisplay(appState);
        });
    }
    
    // Field selector
    if (uiElements.fieldSelector) {
        uiElements.fieldSelector.addEventListener('change', () => {
            const fieldId = uiElements.fieldSelector.value;
            
            // Update app state
            appState.selectedFieldId = fieldId;
            
            // Notify callback
            if (controlChangeCallback) {
                controlChangeCallback('selectedFieldId', fieldId);
            }
        });
    }
    
    // Threat info panel close button
    if (uiElements.threatInfoClose) {
        uiElements.threatInfoClose.addEventListener('click', () => {
            uiElements.threatInfoPanel.style.display = 'none';
        });
    }
    
    // Add keyboard controls
    document.addEventListener('keydown', (event) => {
        // ESC key closes panels
        if (event.key === 'Escape') {
            uiElements.threatInfoPanel.style.display = 'none';
        }
        
        // Number keys for view modes
        if (event.key === '1') {
            // Trigger click on first view mode button
            uiElements.viewModeButtons[0].click();
        } else if (event.key === '2') {
            // Trigger click on second view mode button
            uiElements.viewModeButtons[1].click();
        } else if (event.key === '3') {
            // Trigger click on third view mode button
            uiElements.viewModeButtons[2].click();
        }
    });
}

// Populate field selector with available fields
async function populateFieldSelector() {
    try {
        // In production this would fetch from an API
        const fields = [
            { id: 'field1', name: 'North Wheat Field', threatCount: 12 },
            { id: 'field2', name: 'South Corn Field', threatCount: 8 },
            { id: 'field3', name: 'East Orchard', threatCount: 15 }
        ];
        
        // Clear existing options
        uiElements.fieldSelector.innerHTML = '';
        
        // Add options for each field
        fields.forEach(field => {
            const option = document.createElement('option');
            option.value = field.id;
            option.textContent = `${field.name} (${field.threatCount} threats)`;
            uiElements.fieldSelector.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading fields:', error);
    }
}

// Update date and weather display
function updateDateTime() {
    // Get current date and time
    const now = new Date();
    
    // Format date and time
    const dateOptions = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
    const timeOptions = { hour: '2-digit', minute: '2-digit' };
    
    const dateStr = now.toLocaleDateString('en-US', dateOptions);
    const timeStr = now.toLocaleTimeString('en-US', timeOptions);
    
    // Update display
    uiElements.dateTime.textContent = `${dateStr} ${timeStr}`;
    
    // In a real app, we would fetch weather data from an API
    // For now, we'll use mock data
    uiElements.weatherInfo.innerHTML = `
        <div>72°F</div>
        <div>Sunny</div>
        <div>Humidity: 45%</div>
    `;
}

// Update statistics display based on current filters
function updateStatsDisplay(appState) {
    // In a real app, this data would be calculated based on the actual filtered threats
    // For now, we'll use mock data
    
    // Calculate values based on filters
    let threatCount = 0;
    let affectedArea = 0;
    
    // Base counts - these would come from real data
    const baseCounts = {
        fungal: { count: 5, area: 125 },
        bacterial: { count: 3, area: 85 },
        viral: { count: 2, area: 40 },
        pest: { count: 4, area: 95 }
    };
    
    // Add up counts based on selected threat types
    for (const [type, selected] of Object.entries(appState.selectedThreats)) {
        if (selected && baseCounts[type]) {
            threatCount += baseCounts[type].count;
            affectedArea += baseCounts[type].area;
        }
    }
    
    // Apply severity filter (simplified approximation)
    if (appState.activeThreatFilter !== 'all') {
        // Apply reduction factor based on severity
        const reductionFactor = appState.activeThreatFilter === 'high' ? 0.3 :
                              appState.activeThreatFilter === 'medium' ? 0.4 : 0.3;
        
        threatCount = Math.floor(threatCount * reductionFactor);
        affectedArea = Math.floor(affectedArea * reductionFactor);
    }
    
    // Apply time range filter (simplified approximation)
    // Assume default range is 30 days
    const timeRatio = appState.timeRange / 30;
    threatCount = Math.floor(threatCount * timeRatio);
    affectedArea = Math.floor(affectedArea * timeRatio);
    
    // Calculate field health percentage (inverse of affected area percentage)
    // Assume total field area is 10000 sq m
    const totalArea = 10000;
    const healthPercentage = 100 - Math.min(100, Math.floor((affectedArea / totalArea) * 100));
    
    // Update display
    uiElements.statValues.threats.textContent = threatCount;
    uiElements.statValues.affected.textContent = `${affectedArea}m²`;
    uiElements.statValues.health.textContent = `${healthPercentage}%`;
    
    // Set color for health percentage based on value
    if (healthPercentage > 75) {
        uiElements.statValues.health.style.color = 'var(--success-color)';
    } else if (healthPercentage > 50) {
        uiElements.statValues.health.style.color = 'var(--warning-color)';
    } else {
        uiElements.statValues.health.style.color = 'var(--danger-color)';
    }
}

// Handle user events from UI controls
function handleControlEvents(event) {
    // Event handling logic
}

// Export functions
export {
    initializeControls,
    handleControlEvents
};
