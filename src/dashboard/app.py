import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import os
import sys

# Add components directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import dashboard components
from dashboard.components.map import display_threat_map
from dashboard.components.alerts import display_alerts, display_alert_details
from dashboard.components.analytics import display_analytics, display_forecast
from dashboard.components.image_analysis import display_image_analysis_tool
from dashboard.components.companion_planting import display_companion_planting_optimizer
from dashboard.api_client import AgriDefenderAPI

# Configure the page
st.set_page_config(
    page_title="AgriDefender - Crop Defense Monitoring System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API client
@st.cache_resource
def get_api_client():
    api_url = os.getenv("API_URL", "http://localhost:8000")
    return AgriDefenderAPI(api_url)

api_client = get_api_client()

# Custom CSS with enhanced design system
st.markdown("""
<style>
    /* Color palette */
    :root {
        --primary-color: #2E7D32;        /* Dark green */
        --primary-light: #60ad5e;         /* Light green */
        --primary-dark: #005005;         /* Darker green */
        --secondary-color: #1976D2;      /* Blue */
        --secondary-light: #63a4ff;      /* Light blue */
        --accent-color: #FFC107;          /* Amber */
        --danger-color: #D32F2F;          /* Red */
        --warning-color: #FF9800;         /* Orange */
        --success-color: #43A047;         /* Green */
        --info-color: #0288D1;            /* Light blue */
        --gray-light: #F5F7FA;            /* Light gray background */
        --gray-medium: #E4E7EB;           /* Medium gray borders */
        --gray-dark: #5A6772;             /* Dark gray text */
        --white: #FFFFFF;                 /* White */
        --black: #212121;                 /* Near black */
    }
    
    /* Typography */
    body {
        font-family: 'Inter', sans-serif;
        color: var(--black);
        background-color: var(--white);
    }
    
    .main-header {
        font-size: 2.6rem;
        font-weight: 700;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary-light);
    }
    
    .sub-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: var(--primary-dark);
        margin-bottom: 1.2rem;
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--secondary-color);
        margin-bottom: 1rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid var(--gray-medium);
    }
    
    /* Components */
    .stat-box {
        background-color: var(--white);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--gray-medium);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stat-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.12);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--secondary-color);
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: var(--gray-dark);
        margin-top: 5px;
    }
    
    /* Alert styles */
    .alert-critical {
        background-color: #FDECEA;
        border-left: 5px solid var(--danger-color);
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 4px 4px 0;
    }
    
    .alert-high {
        background-color: #FFF3E0;
        border-left: 5px solid var(--warning-color);
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 4px 4px 0;
    }
    
    .alert-medium {
        background-color: #FFF8E1;
        border-left: 5px solid var(--accent-color);
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 4px 4px 0;
    }
    
    .alert-low {
        background-color: #E8F5E9;
        border-left: 5px solid var(--success-color);
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 4px 4px 0;
    }
    
    /* Cards */
    .card {
        background-color: var(--white);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid var(--gray-medium);
    }
    
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 15px;
        color: var(--primary-dark);
    }
    
    /* Data visualization elements */
    .viz-container {
        background-color: var(--white);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid var(--gray-medium);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        color: var(--gray-dark);
        font-size: 0.8rem;
        border-top: 1px solid var(--gray-medium);
    }
    
    /* Override Streamlit elements */
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.3rem 1rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: var(--primary-dark);
    }
    
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 4px;
        border: 1px solid var(--gray-medium);
    }
    
    /* Sidebar styling */
    .css-1aumxhk {
        background-color: var(--gray-light);
    }
</style>
""", unsafe_allow_html=True)

# Create improved sidebar navigation with icons and better organization
def render_sidebar():
    # Create logo placeholder with better styling
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #2E7D32; font-size: 1.8rem; margin-bottom: 0;">🌱 AgriDefender</h1>
        <p style="font-size: 0.9rem; color: #5A6772; margin-top: 5px;">Crop Defense System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add user profile section
    st.sidebar.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px; background-color: #F5F7FA; padding: 10px; border-radius: 5px;">
        <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #60ad5e; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">JD</div>
        <div style="margin-left: 10px;">
            <div style="font-weight: 500;">John Doe</div>
            <div style="font-size: 0.8rem; color: #5A6772;">Farm Manager</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced navigation menu with icons
    st.sidebar.markdown("### Main Navigation")
    
    # Define menu items with icons
    menu_items = [
        {"icon": "📊", "name": "Dashboard", "desc": "Overview of all threats"},
        {"icon": "🗺️", "name": "Threat Map", "desc": "Geospatial view of threats"},
        {"icon": "🚨", "name": "Alerts", "desc": "Critical notifications"},
        {"icon": "📈", "name": "Analytics", "desc": "Data insights & trends"},
        {"icon": "🔮", "name": "Forecast", "desc": "Predictive analysis"},
    ]
    
    # Tools menu items
    tool_items = [
        {"icon": "🔍", "name": "AI Diagnostic Assistant", "desc": "Analyze plant images"},
        {"icon": "🌿", "name": "Companion Planting", "desc": "Optimize plant combinations"},
        {"icon": "⚙️", "name": "Settings", "desc": "System configuration"}
    ]
    
    # Display main menu
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        selection = st.radio(
            "",
            [item["name"] for item in menu_items],
            label_visibility="collapsed",
            key="main_nav"
        )
    
    # Display tools menu
    st.sidebar.markdown("### Tools")
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        tool_selection = st.radio(
            "",
            [item["name"] for item in tool_items],
            label_visibility="collapsed",
            key="tools_nav"
        )
    
    # Combine selections
    page = selection if selection not in [item["name"] for item in tool_items] else tool_selection
    
    # Add region and crop type filters
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filters")
    
    # Region filter with search
    region = st.sidebar.selectbox(
        "Region",
        ["All Regions", "North Field", "South Plantation", "East Orchard", "West Greenhouse"],
        key="region_filter"
    )
    
    # Crop type multiselect
    crop_types = st.sidebar.multiselect(
        "Crop Types",
        ["Wheat", "Corn", "Soybeans", "Cotton", "Rice", "Potatoes", "Tomatoes"],
        default=["Wheat", "Corn"],
        key="crop_filter"
    )
    
    # Date range with better UI
    st.sidebar.markdown("#### Time Period")
    date_option = st.sidebar.radio(
        "Select time range:",
        ["Last 7 days", "Last 30 days", "Custom range"],
        key="date_option"
    )
    
    if date_option == "Last 7 days":
        date_range = (datetime.now() - timedelta(days=7), datetime.now())
    elif date_option == "Last 30 days":
        date_range = (datetime.now() - timedelta(days=30), datetime.now())
    else:  # Custom range
        date_range = st.sidebar.date_input(
            "Custom date range",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            key="date_filter"
        )
        
    # Weather data integration toggle - from research
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Data Integration")
    weather_data = st.sidebar.toggle("Include weather data in analysis", value=True)
    satellite_imagery = st.sidebar.toggle("Include satellite imagery", value=False)
    
    threat_types = st.sidebar.multiselect(
        "Threat Types",
        ["FUNGAL", "BACTERIAL", "VIRAL", "PEST", "BIOWEAPON", "UNKNOWN"],
        default=["FUNGAL", "BACTERIAL", "VIRAL", "PEST"],
        key="threat_type_filter"
    )
    
    severity_levels = st.sidebar.multiselect(
        "Severity Levels",
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default=["CRITICAL", "HIGH", "MEDIUM"],
        key="severity_filter"
    )
    
    st.sidebar.markdown("---")
    refresh_rate = st.sidebar.slider(
        "Refresh Rate (seconds)",
        min_value=30,
        max_value=300,
        value=60,
        step=30
    )
    
    if st.sidebar.button("Refresh Data"):
        st.experimental_rerun()
    
    # Add a footer to the sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """<div class="footer">
        AgriDefender v0.1.0<br>
        © 2025 Crop Defense Initiative
        </div>""",
        unsafe_allow_html=True
    )
    
    return {
        "page": page,
        "date_range": date_range,
        "threat_types": threat_types,
        "severity_levels": severity_levels,
        "refresh_rate": refresh_rate
    }

# Create dashboard overview with modern card-based layout
def render_dashboard_overview():
    st.markdown('<h1 class="main-header">AgriDefender Dashboard</h1>', unsafe_allow_html=True)
    
    # Welcome message with system status
    st.markdown("""
    <div class="card" style="border-left: 4px solid #2E7D32; margin-bottom: 25px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h3 style="margin: 0; color: #2E7D32;">Welcome to AgriDefender</h3>
                <p style="margin: 5px 0 0 0;">Your comprehensive system for detecting, monitoring, predicting, and responding to biological threats to agriculture.</p>
            </div>
            <div style="background-color: #E8F5E9; padding: 8px 15px; border-radius: 20px; display: flex; align-items: center;">
                <span style="height: 10px; width: 10px; background-color: #43A047; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
                <span style="font-weight: 500; color: #1B5E20;">System Operational</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display summary statistics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Get summary data from API
    try:
        summary_data = api_client.get_summary_statistics(days=30)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <h2>{summary_data.get('total_threats_detected', 0)}</h2>
                <p>Threats Detected</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            active_threats = sum(1 for t in summary_data.get('threats_by_type', {}).values())
            st.markdown(f"""
            <div class="stat-box">
                <h2>{active_threats}</h2>
                <p>Active Threats</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            regions_affected = len(summary_data.get('most_affected_regions', []))
            st.markdown(f"""
            <div class="stat-box">
                <h2>{regions_affected}</h2>
                <p>Regions Affected</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="stat-box">
                <h2>{summary_data.get('average_detection_confidence', 0.0):.0%}</h2>
                <p>Avg. Confidence</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error fetching summary data: {str(e)}")
    
    # Feature sections with card layout and clear CTAs
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Threat Map with enhanced visualization
        st.markdown('<div class="section-title">🗺️ Real-time Threat Map</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card" style="padding: 0; overflow: hidden; margin-bottom: 20px;">
            <div style="padding: 15px 20px; background-color: #F5F7FA; border-bottom: 1px solid #E4E7EB;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 500; color: #212121;">Geographic Distribution of Active Threats</div>
                    <div style="font-size: 0.8rem; color: #5A6772;">Last updated: 5 min ago</div>
                </div>
            </div>
            <div style="padding: 10px 20px;">
        """, unsafe_allow_html=True)
        
        # Display the actual threat map
        try:
            map_data = api_client.get_threats()
            display_threat_map(map_data, height=400)
        except Exception as e:
            st.error(f"Error displaying threat map: {str(e)}")
        
        st.markdown("""
            </div>
            <div style="padding: 10px 20px; border-top: 1px solid #E4E7EB; text-align: right;">
                <a href="#" style="text-decoration: none; color: #1976D2; font-size: 0.9rem; font-weight: 500;">View detailed map →</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Recent alerts with better styling
        st.markdown('<div class="section-title">🚨 Recent Alerts</div>', unsafe_allow_html=True)
        
        # Mock data for recent alerts with improved data
        alerts = [
            {"id": "ALT-001", "title": "Stem rust infection detected", "region": "North Field", "level": "HIGH", "time": "1 hour ago", "pathogen": "Puccinia graminis"},
            {"id": "ALT-002", "title": "Aphid infestation risk", "region": "South Plantation", "level": "MEDIUM", "time": "3 hours ago", "pathogen": "Rhopalosiphum padi"},
            {"id": "ALT-003", "title": "Fungal spread risk", "region": "East Orchard", "level": "HIGH", "time": "5 hours ago", "pathogen": "Botrytis cinerea"},
        ]
        
        # Display alerts with more detailed, actionable information
        for alert in alerts:
            level_class = f"alert-{alert['level'].lower()}"
            icon = "🔴" if alert['level'] == "HIGH" else "🟠" if alert['level'] == "MEDIUM" else "🟢"
            
            st.markdown(f"""
            <div class="{level_class}" style="display: flex; align-items: center;">
                <div style="margin-right: 15px; font-size: 1.5rem;">{icon}</div>
                <div style="flex-grow: 1;">
                    <div style="font-weight: 600; margin-bottom: 2px;">{alert['title']}</div>
                    <div style="font-size: 0.85rem; color: #5A6772;">Pathogen: <span style="font-style: italic;">{alert['pathogen']}</span> | Region: {alert['region']} | {alert['time']}</div>
                </div>
                <div>
                    <a href="#" style="text-decoration: none; background-color: #1976D2; color: white; padding: 5px 10px; border-radius: 4px; font-size: 0.8rem;">View Details</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""<div style="text-align: center; margin: 15px 0;"><a href="#" style="font-size: 0.9rem; color: #1976D2; text-decoration: none;">View all alerts →</a></div>""", unsafe_allow_html=True)
    
    # Feature Toolbox - Incorporating concepts from research
    st.markdown('<div class="section-title" style="margin-top: 30px;">🧰 Research-Based Tools</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card" style="height: 100%; position: relative;">
            <div style="position: absolute; top: -10px; right: -10px; background-color: #FFC107; color: white; border-radius: 20px; padding: 3px 8px; font-size: 0.7rem; font-weight: bold;">RESEARCH</div>
            <h3 style="color: #1976D2; font-size: 1.2rem; margin-bottom: 10px;">🔍 AI Diagnostic Assistant</h3>
            <p style="font-size: 0.9rem; color: #5A6772; margin-bottom: 15px;">Upload images to identify plant diseases with our deep learning model.</p>
            <p style="font-size: 0.8rem; margin-bottom: 15px;"><strong>Accuracy:</strong> 93% for 38 crop diseases</p>
            <a href="#" style="text-decoration: none; color: white; background-color: #1976D2; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; display: inline-block;">Launch Tool</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Notification Settings")
        st.checkbox("Email Notifications", value=True)
        st.checkbox("SMS Notifications", value=False)
        st.checkbox("Push Notifications", value=True)
        
        st.subheader("Alert Thresholds")
        st.select_slider("Minimum Alert Severity", options=["LOW", "MEDIUM", "HIGH", "CRITICAL"], value="MEDIUM")
        st.slider("Minimum Confidence Threshold", min_value=0.0, max_value=1.0, value=0.7, step=0.05, format="%.2f")

if __name__ == "__main__":
    main()
