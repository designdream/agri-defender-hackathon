#!/usr/bin/env python3
"""
AgriDefender Demo Script

This is a simplified demonstration of the AgriDefender system for crop defense monitoring.
It shows the key visualization and analytical capabilities of the system.
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import datetime
import random

# Set page configuration
st.set_page_config(
    page_title="AgriDefender Demo",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1B5E20;
        margin-bottom: 1rem;
    }
    .stat-box {
        background-color: #f0f8ff;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 5px solid #c62828;
        padding: 10px;
        margin-bottom: 10px;
    }
    .alert-medium {
        background-color: #fff8e1;
        border-left: 5px solid #f9a825;
        padding: 10px;
        margin-bottom: 10px;
    }
    .alert-low {
        background-color: #e8f5e9;
        border-left: 5px solid #388e3c;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
def render_sidebar():
    st.sidebar.title("AgriDefender")
    st.sidebar.markdown("### Crop Defense Monitoring System")
    
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio(
        "Select a page:",
        ["Dashboard", "Threat Map", "Analytics", "Bioterrorism Detection"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## Filters")
    
    threat_types = st.sidebar.multiselect(
        "Threat Types",
        ["FUNGAL", "BACTERIAL", "VIRAL", "PEST"],
        default=["FUNGAL", "BACTERIAL", "VIRAL", "PEST"]
    )
    
    severity_levels = st.sidebar.multiselect(
        "Severity Levels",
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default=["CRITICAL", "HIGH", "MEDIUM"]
    )
    
    regions = st.sidebar.multiselect(
        "Regions",
        ["Central Texas", "Southeast Texas", "West Texas", "North Texas", "South Texas"],
        default=["Central Texas", "Southeast Texas"]
    )
    
    return {
        "page": page,
        "threat_types": threat_types,
        "severity_levels": severity_levels,
        "regions": regions
    }

# Mock data generation
def generate_mock_data():
    # Generate mock threat data
    threat_types = ["FUNGAL", "BACTERIAL", "VIRAL", "PEST", "UNKNOWN"]
    threat_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    
    # Center coordinates for Texas
    center_lat, center_lon = 31.0, -100.0
    
    threats = []
    for i in range(20):
        # Generate a random location in Texas
        lat = center_lat + (random.random() - 0.5) * 5
        lon = center_lon + (random.random() - 0.5) * 10
        
        # Assign random threat type and level
        threat_type = random.choice(threat_types)
        
        # Make some threats more severe than others
        if i < 3:
            threat_level = "CRITICAL"
        elif i < 8:
            threat_level = "HIGH"
        elif i < 15:
            threat_level = "MEDIUM"
        else:
            threat_level = "LOW"
        
        # Generate detection time (mostly recent)
        days_ago = int(random.expovariate(0.5))
        detection_time = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).isoformat()
        
        threat = {
            "id": f"threat-{100 + i}",
            "threat_type": threat_type,
            "threat_level": threat_level,
            "detection_time": detection_time,
            "confidence": 0.5 + random.random() / 2,  # Between 0.5 and 1.0
            "location": {"type": "Point", "coordinates": [lon, lat]},
            "description": f"{threat_type} threat detected in {['corn', 'wheat', 'soybean', 'rice'][i % 4]} field"
        }
        threats.append(threat)
    
    return threats

# Display threat map
def display_threat_map(threats, height=500):
    # Create a map centered on Texas
    m = folium.Map(location=[31.0, -100.0], zoom_start=6, tiles="CartoDB positron")
    
    # Define colors for different threat levels
    colors = {
        "CRITICAL": "#c62828",
        "HIGH": "#ef6c00",
        "MEDIUM": "#f9a825",
        "LOW": "#388e3c"
    }
    
    # Add threat markers to the map
    for threat in threats:
        coordinates = threat["location"]["coordinates"]
        lon, lat = coordinates
        color = colors.get(threat["threat_level"], "#1976D2")
        
        # Create popup content
        popup_html = f"""
        <div style="width:200px">
            <h4>{threat["threat_type"]} - {threat["threat_level"]}</h4>
            <p><strong>ID:</strong> {threat["id"]}</p>
            <p><strong>Confidence:</strong> {threat["confidence"]:.1%}</p>
            <p><strong>Description:</strong> {threat["description"]}</p>
        </div>
        """
        
        # Add marker
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{threat['threat_type']} - {threat['threat_level']}",
            icon=folium.Icon(color="red" if threat["threat_level"] in ["CRITICAL", "HIGH"] else "orange", icon="warning-sign")
        ).add_to(m)
    
    # Display the map
    folium_static(m, height=height)

# Display threat statistics
def display_threat_statistics(threats):
    # Count threats by type
    threat_types = {}
    for threat in threats:
        t_type = threat["threat_type"]
        threat_types[t_type] = threat_types.get(t_type, 0) + 1
    
    # Count threats by severity
    threat_levels = {}
    for threat in threats:
        level = threat["threat_level"]
        threat_levels[level] = threat_levels.get(level, 0) + 1
    
    # Display statistics in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Threats by Type")
        fig = px.bar(
            x=list(threat_types.keys()),
            y=list(threat_types.values()),
            color=list(threat_types.keys()),
            labels={"x": "Threat Type", "y": "Count"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Threats by Severity")
        # Order levels from most to least severe
        ordered_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        ordered_counts = [threat_levels.get(level, 0) for level in ordered_levels]
        
        fig = px.bar(
            x=ordered_levels,
            y=ordered_counts,
            color=ordered_levels,
            color_discrete_map={
                "CRITICAL": "#c62828",
                "HIGH": "#ef6c00",
                "MEDIUM": "#f9a825",
                "LOW": "#388e3c"
            },
            labels={"x": "Severity Level", "y": "Count"}
        )
        st.plotly_chart(fig, use_container_width=True)

# Display threat detection visualization
def display_threat_detection():
    st.subheader("Threat Detection Demonstration")
    
    # Create a grid to represent a field
    grid_size = 20
    field = np.zeros((grid_size, grid_size))
    
    # Add some "normal" variation
    for i in range(grid_size):
        for j in range(grid_size):
            field[i, j] = 0.1 + 0.1 * np.sin(i/3) + 0.1 * np.cos(j/3)
    
    # Add an anomaly (simulating a biological threat)
    center_x, center_y = grid_size // 3, grid_size // 3
    for i in range(grid_size):
        for j in range(grid_size):
            dist = np.sqrt((i - center_x)**2 + (j - center_y)**2)
            if dist < 5:
                field[i, j] += 0.8 * (1 - dist/5)
    
    # Create a visualization of the field
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Raw Sensor Data")
        fig = px.imshow(
            field,
            color_continuous_scale='Viridis',
            labels=dict(color="Value"),
            title="Soil Moisture Readings"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Anomaly Detection")
        # Create a mask for detected anomalies
        anomaly_threshold = 0.5
        anomalies = field > anomaly_threshold
        
        # Visualize the anomalies
        fig = px.imshow(
            anomalies.astype(int),
            color_continuous_scale=['white', 'red'],
            labels=dict(color="Anomaly"),
            title="Detected Threat Pattern"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation
    st.markdown("""
    The system detected a potential fungal infection based on abnormal soil moisture patterns.
    The affected area shows a characteristic circular pattern typical of fungal spread.
    """)

# Display bioterrorism detection
def display_bioterrorism_detection():
    st.markdown('<h1 class="main-header">Bioterrorism Detection</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Simulated Bioterrorism Scenario
    
    The system has detected an unusual biological signature that doesn't match known natural disease profiles.
    The pattern of spread and genetic markers suggest potential deliberate introduction.
    """)
    
    # Display alert
    st.markdown("""
    <div class="alert-high">
        <h3>⚠️ CRITICAL ALERT: Potential Bioterrorism Detected</h3>
        <p><strong>Location:</strong> West Texas Agricultural Region</p>
        <p><strong>Detection Time:</strong> 2025-04-26 14:22:31</p>
        <p><strong>Confidence:</strong> 92%</p>
        <p><strong>Description:</strong> Unidentified pathogen with unusual genetic markers detected in multiple locations simultaneously. Spread pattern inconsistent with natural dispersal.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show unusual metrics
    st.subheader("Anomaly Indicators")
    
    metrics = {
        "Unusual Genetic Markers": 0.92,
        "Atypical Spread Pattern": 0.89,
        "Inconsistent with Known Pathogens": 0.78,
        "Multiple Simultaneous Outbreaks": 0.95,
        "Unnatural Concentration Levels": 0.86
    }
    
    # Create a radar chart
    categories = list(metrics.keys())
    values = list(metrics.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Anomaly Metrics',
        line_color='crimson'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show recommendations
    st.subheader("Recommended Actions")
    
    st.markdown("""
    1. **IMMEDIATE NOTIFICATION**: Alert agricultural security authorities
    2. **CONTAINMENT**: Restrict access to affected areas immediately
    3. **SAMPLE COLLECTION**: Deploy hazmat team to collect specimens using Level 3 biosafety protocols
    4. **SURVEILLANCE**: Activate enhanced monitoring in surrounding regions
    5. **DOCUMENTATION**: Record all observations and secure digital evidence
    """)
    
    st.warning("⚠️ DO NOT attempt remediation without expert guidance")

# Main application
def main():
    # Render sidebar and get configuration
    config = render_sidebar()
    
    # Generate mock data
    threats = generate_mock_data()
    
    # Filter threats based on sidebar settings
    filtered_threats = [
        t for t in threats 
        if t["threat_type"] in config["threat_types"] and t["threat_level"] in config["severity_levels"]
    ]
    
    # Display the selected page
    if config["page"] == "Dashboard":
        st.markdown('<h1 class="main-header">AgriDefender Dashboard</h1>', unsafe_allow_html=True)
        st.markdown("## Crop Defense Monitoring System")
        
        # Display summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <h2>{len(threats)}</h2>
                <p>Total Threats</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            critical_high = len([t for t in threats if t["threat_level"] in ["CRITICAL", "HIGH"]])
            st.markdown(f"""
            <div class="stat-box">
                <h2>{critical_high}</h2>
                <p>High Severity</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            regions = len(

