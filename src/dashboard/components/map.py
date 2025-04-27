import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster, Draw
from streamlit_folium import folium_static
import pandas as pd
import json
from typing import List, Dict, Any, Optional

# Define colors for different threat levels
THREAT_COLORS = {
    "CRITICAL": "#c62828",  # Red
    "HIGH": "#ef6c00",      # Orange
    "MEDIUM": "#f9a825",    # Amber
    "LOW": "#388e3c"        # Green
}

# Define icons for different threat types
THREAT_ICONS = {
    "FUNGAL": "bug",
    "BACTERIAL": "flask",
    "VIRAL": "film",
    "PEST": "bug",
    "BIOWEAPON": "warning-sign",
    "UNKNOWN": "question-circle"
}

def display_threat_map(
    threat_data: List[Dict[str, Any]], 
    height: int = 500, 
    show_controls: bool = False
) -> None:
    """
    Display a map with threat locations and affected areas.
    
    Args:
        threat_data: List of threat data objects
        height: Height of the map in pixels
        show_controls: Whether to show additional map controls
    """
    if not threat_data:
        st.info("No threat data available to display on the map.")
        return
    
    # Create a base map centered on the first threat location
    first_threat = threat_data[0]
    first_location = first_threat.get("location", {}).get("coordinates", [-97.7431, 30.2672])  # Default to Austin, TX
    
    # Flip the coordinates since GeoJSON uses [longitude, latitude]
    center_lat, center_lon = first_location[1], first_location[0]
    
    # Create the map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles="CartoDB positron"
    )
    
    # Add other tile layers
    folium.TileLayer("OpenStreetMap").add_to(m)
    folium.TileLayer("CartoDB dark_matter").add_to(m)
    folium.TileLayer("Stamen Terrain").add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add drawing tools if controls are enabled
    if show_controls:
        Draw(
            export=True,
            position="topleft",
            draw_options={
                "polyline": False,
                "rectangle": True,
                "circle": True,
                "marker": False,
                "circlemarker": False
            }
        ).add_to(m)
    
    # Create a marker cluster group for threat points
    marker_cluster = MarkerCluster(name="Threat Locations").add_to(m)
    
    # Create data for heatmap
    heat_data = []
    
    # Process each threat
    for threat in threat_data:
        # Extract threat information
        threat_id = threat.get("id", "unknown")
        threat_type = threat.get("threat_type", "UNKNOWN")
        threat_level = threat.get("threat_level", "LOW")
        description = threat.get("description", "No description available")
        confidence = threat.get("confidence", 0.0)
        detection_time = threat.get("detection_time", "Unknown time")
        
        # Get the location
        location = threat.get("location", {})
        if location.get("type") != "Point":
            continue
            
        coords = location.get("coordinates", [0, 0])
        lon, lat = coords
        
        # Add to heat map data
        # Weight by severity (LOW=0.3, MEDIUM=0.5, HIGH=0.8, CRITICAL=1.0)
        weight = 0.3
        if threat_level == "MEDIUM":
            weight = 0.5
        elif threat_level == "HIGH":
            weight = 0.8
        elif threat_level == "CRITICAL":
            weight = 1.0
            
        # Add to heat data with weight
        heat_data.append([lat, lon, weight])
        
        # Create a marker for the threat
        color = THREAT_COLORS.get(threat_level, "#1976D2")
        icon = THREAT_ICONS.get(threat_type, "info-sign")
        
        popup_html = f"""
        <div style="width:250px">
            <h4>{threat_type} Threat - {threat_level}</h4>
            <p><strong>ID:</strong> {threat_id[:8]}...</p>
            <p><strong>Detected:</strong> {detection_time}</p>
            <p><strong>Confidence:</strong> {confidence:.1%}</p>
            <p><strong>Description:</strong> {description}</p>
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{threat_type} - {threat_level}",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(marker_cluster)
        
        # Add affected area if available
        affected_area = threat.get("affected_area")
        if affected_area and affected_area.get("type") == "Polygon":
            # GeoJSON requires [longitude, latitude] format
            folium.GeoJson(
                affected_area,
                name=f"Affected Area - {threat_id[:8]}",
                style_function=lambda x: {
                    'fillColor': color,
                    'color': color,
                    'weight': 2,
                    'fillOpacity': 0.2
                },
                tooltip=f"Affected area - {threat_type} - {threat_level}"
            ).add_to(m)
    
    # Add heat map layer if we have enough data
    if len(heat_data) > 1:
        HeatMap(
            heat_data,
            name="Threat Heatmap",
            radius=15,
            blur=10,
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1: 'red'},
            min_opacity=0.5
        ).add_to(m)
    
    # Fit bounds to include all threats
    if len(threat_data) > 1:
        try:
            sw = [float('inf'), float('inf')]
            ne = [float('-inf'), float('-inf')]
            
            for threat in threat_data:
                loc = threat.get("location", {}).get("coordinates", [0, 0])
                lon, lat = loc
                
                sw[0] = min(sw[0], lat)
                sw[1] = min(sw[1], lon)
                ne[0] = max(ne[0], lat)
                ne[1] = max(ne[1], lon)
            
            m.fit_bounds([sw, ne])
        except Exception as e:
            st.warning(f"Could not fit map bounds: {str(e)}")
    
    # Display additional controls if requested
    if show_controls:
        # Create columns for map controls
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Map Layers")
            st.info("Use the layer control in the top right corner of the map to toggle different layers.")
            
            st.subheader("Drawing Tools")
            st.info("Use the drawing tools in the top left corner to mark areas of interest.")
            
            # Create toggles for different view options
            show_heatmap = st.checkbox("Show Heat Map", value=True)
            show_clusters = st.checkbox("Cluster Markers", value=True)
            
            # These toggles don't actually change the map in this implementation
            # In a real app, you would need to rebuild the map based on these options
        
        with col2:
            # Display the map in the larger column
            folium_static(m, height=height)
    else:
        # Just display the map without controls
        folium_static(m, height=height)

