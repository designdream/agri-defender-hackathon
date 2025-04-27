import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import altair as alt

def display_alerts(
    alerts_data: List[Dict[str, Any]], 
    show_all_button: bool = False, 
    allow_selection: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Display a list of threat alerts.
    
    Args:
        alerts_data: List of alert data objects
        show_all_button: Whether to show a button to view all alerts
        allow_selection: Whether to allow selection of an alert
        
    Returns:
        Selected alert data if allow_selection is True and an alert is selected, otherwise None
    """
    if not alerts_data:
        st.info("No alerts to display.")
        return None
    
    # Create UI elements based on options
    if show_all_button:
        st.markdown(
            f"<p>Showing {len(alerts_data)} recent alerts. "
            f"<a href='#' target='_self'>View all alerts</a></p>",
            unsafe_allow_html=True
        )
    
    # Display each alert
    selected_alert = None
    
    for i, alert in enumerate(alerts_data):
        # Extract alert information
        alert_id = alert.get("id", "unknown")
        threat_type = alert.get("threat_type", "UNKNOWN")
        threat_level = alert.get("threat_level", "LOW")
        description = alert.get("description", "No description available")
        confidence = alert.get("confidence", 0.0)
        
        # Get timestamp and format it
        detection_time = alert.get("detection_time", "")
        try:
            dt = datetime.fromisoformat(detection_time.replace("Z", "+00:00"))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_time = detection_time
        
        # Determine CSS class based on severity
        css_class = "alert-low"
        if threat_level == "HIGH" or threat_level == "CRITICAL":
            css_class = "alert-high"
        elif threat_level == "MEDIUM":
            css_class = "alert-medium"
        
        # Create alert box with HTML
        alert_html = f"""
        <div class="{css_class}">
            <div style="display: flex; justify-content: space-between;">
                <strong>{threat_type} - {threat_level}</strong>
                <span>{formatted_time}</span>
            </div>
            <p>{description}</p>
            <div style="display: flex; justify-content: space-between;">
                <span>ID: {alert_id[:8]}...</span>
                <span>Confidence: {confidence:.1%}</span>
            </div>
        </div>
        """
        
        st.markdown(alert_html, unsafe_allow_html=True)
        
        # If selection is allowed, add a button
        if allow_selection:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button(f"View Details", key=f"alert_{i}"):
                    selected_alert = alert
    
    return selected_alert


def display_alert_details(alert: Dict[str, Any]) -> None:
    """
    Display detailed information about a specific alert.
    
    Args:
        alert: Alert data object
    """
    # Extract alert information
    alert_id = alert.get("id", "unknown")
    threat_type = alert.get("threat_type", "UNKNOWN")
    threat_level = alert.get("threat_level", "LOW")
    description = alert.get("description", "No description available")
    confidence = alert.get("confidence", 0.0)
    
    # Get timestamp and format it
    detection_time = alert.get("detection_time", "")
    try:
        dt = datetime.fromisoformat(detection_time.replace("Z", "+00:00"))
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        formatted_time = detection_time
    
    # Get recommendations
    recommendations = alert.get("recommendations", [])
    
    # Get source data
    source_data = alert.get("source_data", [])
    
    # Display alert details
    st.markdown(f"## Alert Details: {threat_type} Threat")
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display main information
        st.markdown(f"**ID:** {alert_id}")
        st.markdown(f"**Type:** {threat_type}")
        st.markdown(f"**Severity:** {threat_level}")
        st.markdown(f"**Confidence:** {confidence:.1%}")
        st.markdown(f"**Detected:** {formatted_time}")
        st.markdown(f"**Description:** {description}")
        
        # Display recommendations
        if recommendations:
            st.markdown("### Recommended Actions")
            for i, rec in enumerate(recommendations):
                st.markdown(f"{i+1}. {rec}")
        
        # Display source data
        if source_data:
            st.markdown("### Source Data")
            st.markdown(", ".join(source_data))
    
    with col2:
        # Display a map with the threat location
        st.markdown("### Location")
        
        location = alert.get("location", {})
        if location.get("type") == "Point":
            coords = location.get("coordinates", [0, 0])
            lon, lat = coords
            
            # Display a simple static map
            st.map(pd.DataFrame({
                'lat': [lat],
                'lon': [lon]
            }))
        else:
            st.info("Location data not available")
        
        # Display confidence gauge
        st.markdown("### Detection Confidence")
        
        # Create a gauge chart using Altair
        gauge_df = pd.DataFrame({'value': [confidence]})
        
        gauge_chart = alt.Chart(gauge_df).mark_arc(
            innerRadius=50,
            outerRadius=60,
            startAngle=-3.14159/2,
            endAngle=3.14159/2
        ).encode(
            theta=alt.Theta(
                'value:Q',
                scale=alt.Scale(domain=[0, 1])
            ),
            color=alt.Color(
                'value:Q',
                scale=alt.Scale(
                    domain=[0, 0.4, 0.7, 1],
                    range=['red', 'orange', 'yellow', 'green']
                ),
                legend=None
            )
        ).properties(width=200, height=100)
        

