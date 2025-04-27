import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

def display_analytics(analytics_data: Dict[str, Any]) -> None:
    """
    Display analytics dashboards with various charts and visualizations.
    
    Args:
        analytics_data: Dictionary containing analytics data
    """
    if not analytics_data:
        st.info("No analytics data available.")
        return
    
    # Extract the time period from the data
    time_period = analytics_data.get("time_period", "Unknown time period")
    st.subheader(f"Analytics for {time_period}")
    
    # Create tabs for different analytics views
    tab1, tab2, tab3 = st.tabs(["Threat Overview", "Geographical Analysis", "Trend Analysis"])
    
    with tab1:
        display_threat_overview(analytics_data)
    
    with tab2:
        display_geographical_analysis(analytics_data)
    
    with tab3:
        display_trend_analysis(analytics_data)


def display_threat_overview(analytics_data: Dict[str, Any]) -> None:
    """
    Display charts showing threat types and severity distribution.
    
    Args:
        analytics_data: Dictionary containing analytics data
    """
    # Get threat counts by type and level
    threat_counts = analytics_data.get("threat_counts", {})
    threat_levels = analytics_data.get("threat_levels", {})
    
    if not threat_counts or not threat_levels:
        st.info("No threat overview data available.")
        return
    
    # Create two columns for the charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Threats by Type")
        
        # Create DataFrame for the chart
        df_types = pd.DataFrame({
            "Threat Type": list(threat_counts.keys()),
            "Count": list(threat_counts.values())
        })
        
        # Sort by count
        df_types = df_types.sort_values("Count", ascending=False)
        
        # Create bar chart with Plotly for better interactivity
        fig = px.bar(
            df_types,
            x="Threat Type",
            y="Count",
            color="Threat Type",
            text="Count",
            title="Distribution of Threats by Type"
        )
        
        fig.update_layout(
            xaxis_title="Threat Type",
            yaxis_title="Number of Threats",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Threats by Severity")
        
        # Create DataFrame for the chart
        df_levels = pd.DataFrame({
            "Severity Level": list(threat_levels.keys()),
            "Count": list(threat_levels.values())
        })
        
        # Sort by severity (CRITICAL, HIGH, MEDIUM, LOW)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        df_levels["order"] = df_levels["Severity Level"].map(severity_order)
        df_levels = df_levels.sort_values("order")
        df_levels = df_levels.drop("order", axis=1)
        
        # Define colors for severity levels
        severity_colors = {
            "CRITICAL": "#c62828",
            "HIGH": "#ef6c00",
            "MEDIUM": "#f9a825",
            "LOW": "#388e3c"
        }
        
        # Create bar chart with Plotly
        fig = px.bar(
            df_levels,
            x="Severity Level",
            y="Count",
            color="Severity Level",
            text="Count",
            color_discrete_map=severity_colors,
            title="Distribution of Threats by Severity"
        )
        
        fig.update_layout(
            xaxis_title="Severity Level",
            yaxis_title="Number of Threats",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Display a sunburst chart for threat types and severity combined
    st.subheader("Threat Types by Severity")
    
    # Create mock data for the visualization
    # In a real implementation, this would come from the API
    # Here we generate some random but believable numbers
    mock_threat_severity = [
        {"threat_type": "FUNGAL", "severity": "LOW", "count": 10},
        {"threat_type": "FUNGAL", "severity": "MEDIUM", "count": 12},
        {"threat_type": "FUNGAL", "severity": "HIGH", "count": 5},
        {"threat_type": "FUNGAL", "severity": "CRITICAL", "count": 1},
        {"threat_type": "BACTERIAL", "severity": "LOW", "count": 6},
        {"threat_type": "BACTERIAL", "severity": "MEDIUM", "count": 4},
        {"threat_type": "BACTERIAL", "severity": "HIGH", "count": 2},
        {"threat_type": "VIRAL", "severity": "LOW", "count": 2},
        {"threat_type": "VIRAL", "severity": "MEDIUM", "count": 2},
        {"threat_type": "VIRAL", "severity": "HIGH", "count": 1},
        {"threat_type": "PEST", "severity": "LOW", "count": 20},
        {"threat_type": "PEST", "severity": "MEDIUM", "count": 12},
        {"threat_type": "PEST", "severity": "HIGH", "count": 3},
        {"threat_type": "UNKNOWN", "severity": "LOW", "count": 5},
        {"threat_type": "UNKNOWN", "severity": "MEDIUM", "count": 2}
    ]
    
    # Create DataFrame for the sunburst chart
    df_sunburst = pd.DataFrame(mock_threat_severity)
    
    # Create sunburst chart with Plotly
    fig = px.sunburst(
        df_sunburst,
        path=["threat_type", "severity"],
        values="count",
        color="severity",
        color_discrete_map={
            "LOW": "#388e3c",
            "MEDIUM": "#f9a825",
            "HIGH": "#ef6c00",
            "CRITICAL": "#c62828"
        },
        title="Threat Distribution by Type and Severity"
    )
    
    fig.update_layout(height=500)
    
    st.plotly_chart(fig, use_container_width=True)


def display_geographical_analysis(analytics_data: Dict[str, Any]) -> None:
    """
    Display geographical analysis of threats.
    
    Args:
        analytics_data: Dictionary containing analytics data
    """
    # Get hotspots data
    hotspots = analytics_data.get("hotspots", [])
    
    if not hotspots:
        st.info("No geographical data available.")
        return
    
    st.subheader("Threat Hotspots")
    
    # Create a DataFrame for the hotspots
    hotspot_data = []
    for hotspot in hotspots:
        props = hotspot.get("properties", {})
        coords = hotspot.get("geometry", {}).get("coordinates", [0, 0])
        
        hotspot_data.append({
            "region": props.get("region", "Unknown"),
            "intensity": props.get("intensity", 0),
            "threat_count": props.get("threat_count", 0),
            "lon": coords[0],
            "lat": coords[1]
        })
    
    df_hotspots = pd.DataFrame(hotspot_data)
    
    # Display a map of hotspots
    st.subheader("Threat Hotspot Map")
    
    # Create a Plotly scatter mapbox
    fig = px.scatter_mapbox(
        df_hotspots,
        lat="lat",
        lon="lon",
        size="threat_count",
        color="intensity",
        color_continuous_scale=px.colors.sequential.Reds,
        hover_name="region",
        hover_data=["threat_count", "intensity"],
        zoom=5,
        height=600,
        title="Threat Hotspots by Region"
    )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0, "t":40, "l":0, "b":0}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display regional distribution table
    st.subheader("Regional Threat Distribution")
    
    # Sort by threat count
    df_hotspots = df_hotspots.sort_values("threat_count", ascending=False)
    
    # Format table
    table_data = df_hotspots[["region", "threat_count", "intensity"]].copy()
    table_data["intensity"] = table_data["intensity"].apply(lambda x: f"{x:.1%}")
    table_data.columns = ["Region", "Number of Threats", "Intensity"]
    
    st.table(table_data)


def display_trend_analysis(analytics_data: Dict[str, Any]) -> None:
    """
    Display trend analysis visualizations.
    
    Args:
        analytics_data: Dictionary containing analytics data
    """
    # Get trends data
    trends = analytics_data.get("trends", {})
    
    if not trends:
        st.info("No trend data available.")
        return
    
    st.subheader("Threat Trends Over Time")
    
    # Create a DataFrame for the trends
    # First, create dates for the x-axis (assuming last 5 days)
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(4, -1, -1)]
    
    # Create the DataFrame with dates and trend values
    df_trends = pd.DataFrame({"Date": dates})
    
    # Add each trend as a column
    for trend_name, trend_values in trends.items():
        if len(trend_values) == len(dates):
            df_trends[trend_name] = trend_values
    
    # Melt the DataFrame for easier plotting
    df_melted = df_trends.melt(
        id_vars=["Date"],
        var_name="Trend",
        value_name="Value"
    )
    
    # Create a line chart with Plotly
    fig = px.line(
        df_melted,
        x="Date",
        y="Value",
        color="Trend",
        markers=True,
        title="Trend Analysis Over Time"
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Value",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display individual trend charts
    st.subheader("Individual Trend Analysis")
    
    # Create columns for individual trend charts
    cols = st.columns(len(trends))
    
    # Create a chart for each trend
    for i, (trend_name, trend_values) in enumerate(trends.items()):
        with cols[i % len(cols)]:
            # Clean up the trend name for display
            display_name = trend_name.replace("_", " ").title()
            
            # Create a simple trend chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=trend_values,
                mode="lines+markers",
                name=display_name,
                line=dict(width=3, color="#1976D2"),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title=display_name,
                xaxis_title="Date",
                yaxis_title="Value",
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate and display trend change
            if len(trend_values) >= 2:
                change = trend_values[-1] - trend_values[0]
                percent_change = (change / trend_values[0]) * 100 if trend_values[0] else 0
                
                change_text = "Increase" if change >= 0 else "Decrease"
                change_color = "green" if change >= 0 else "red"
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <p>
                        {change_text}: 
                        <span style="color: {change_color}; font-weight: bold;">
                            {abs(percent_change):.1f}%
                        </span>
                    </p>
                </div>
                """, unsafe_allow_html=True)


def display_forecast(
    selected_threat: Dict[str, Any],
    forecast_data: List[Dict[str, Any]]
) -> None:
    """
    Display forecast visualizations for a selected threat.
    
    Args:
        selected_threat: Dictionary with information about the selected threat
        forecast_data: List of forecast data points for the threat
    """
    if not selected_threat or not forecast_data:
        st.info("No forecast data available.")
        return
    
    # Extract threat information
    threat_id = selected_threat.get("id", "unknown")
    threat_type = selected_threat.get("threat_type", "UNKNOWN")
    initial_level = selected_threat.get("threat_level", "LOW")
    
    st.subheader(f"Forecast for {threat_type} Threat")
    
    # Display initial threat information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Threat Type", threat_type)
    
    with col2:
        st.metric("Initial Severity", initial_level)
    
    with col3:
        detection_time = selected_threat.get("detection_time", "Unknown")
        st.metric("Detection Time", detection_time)
    
    # Create a DataFrame for the forecast
    forecast_rows = []
    
    for pred in forecast_data:
        # Extract prediction data
        prediction_time = pred.get("prediction_time", "")
        try:
            dt = datetime.fromisoformat(prediction_time.replace("Z", "+00:00"))
            formatted_time = dt.strftime("%Y-%m-%d")
        except:
            formatted_time = prediction_time
        
        threat_level = pred.get("threat_level", "UNKNOWN")
        confidence = pred.get("confidence", 0.0)
        probability = pred.get("probability", 0.0)
        spread_velocity = pred.get("spread_velocity", 0.0)
        day = pred.get("day", 0)
        
        # Add to rows
        forecast_rows.append({
            "Day": day,
            "Date": formatted_time,
            "Threat Level": threat_level,
            "Confidence": confidence,
            "Probability": probability,
            "Spread Velocity (m/day)": spread_velocity
        })
    
    # Create DataFrame and display as table
    if forecast_rows:
        df_forecast = pd.DataFrame(forecast_rows)
        
        # Format confidence and probability columns
        df_forecast["Confidence"] = df_forecast["Confidence"].apply(lambda x: f"{x:.1%}")
        df_forecast["Probability"] = df_forecast["Probability"].apply(lambda x: f"{x:.1%}")
        
        st.dataframe(df_forecast)
    
    # Create a visualization of the forecast severity progression
    st.subheader("Threat Severity Progression")
    
    # Extract days and severity levels
    days = [pred.get("day", 0) for pred in forecast_data]
    severity_values = []
    
    # Map severity levels to numeric values for visualization
    severity_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    
    for pred in forecast_data:
        level = pred.get("threat_level", "LOW")
        severity_values.append(severity_map.get(level, 1))
    
    # Create a DataFrame for the chart
    df_severity = pd.DataFrame({
        "Day": days,
        "Severity": severity_values
    })
    
    # Create line chart with Plotly
    fig = px.line(
        df_severity,
        x="Day",
        y="Severity",
        markers=True,
        title="Forecast Threat Severity Progression"
    )
    
    # Update y-axis to show severity labels
    fig.update_layout(
        xaxis_title="Days from Detection",
        yaxis_title="Severity Level",
        yaxis=dict(
            tickmode="array",
            tickvals=[1, 2, 3, 4],
            ticktext=["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        ),
        height=400
    )
    
    # Customize line appearance
    fig.update_traces(
        line=dict(width=3, color="#ef6c00"),
        marker=dict(size=10, color="#ef6c00")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display spread visualization on a map if location data is available
    st.subheader("Spread Visualization")
    
    # Create columns for displaying multiple maps
    map_col1, map_col2 = st.columns(2)
    
    # Get initial location from the selected threat
    initial_location = selected_threat.get("location", {}).get("coordinates", [0, 0])
    if initial_location:
        lon, lat = initial_location
        
        with map_col1:
            st.caption("Initial Detection Area")
            initial_df = pd.DataFrame({
                'lat': [lat],
                'lon': [lon],
                'size': [500]  # Size for initial detection point
            })
            
            # Show initial detection point
            fig = px.scatter_mapbox(
                initial_df,
                lat="lat",
                lon="lon",
                size="size",
                size_max=15,
                zoom=10,
                height=400,
                color_discrete_sequence=["#c62828"]
            )
            
            fig.update_layout(
                mapbox_style="carto-positron",
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with map_col2:
            st.caption("Predicted Final Spread (Day 7)")
            
            # Get the last prediction for the final spread
            final_pred = forecast_data[-1] if forecast_data else None
            
            if final_pred:
                final_location = final_pred.get("location", {}).get("coordinates", [0, 0])
                final_lon, final_lat = final_location
                
                # Create circles for initial and final detection
                circles_df = pd.DataFrame({
                    'lat': [lat, final_lat],
                    'lon': [lon, final_lon],
                    'size': [500, 2000],  # Smaller for initial, larger for final
                    'color': ['Initial', 'Final']
                })
                
                # Show both circles
                fig = px.scatter_mapbox(
                    circles_df,
                    lat="lat",
                    lon="lon",
                    size="size",
                    color="color",
                    size_max=40,
                    zoom=9,
                    height=400,
                    color_discrete_map={
                        'Initial': '#c62828',
                        'Final': '#ef6c00'
                    }
                )
                
                fig.update_layout(
                    mapbox_style="carto-positron",
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Display recommended actions
    st.subheader("Recommended Actions")
    
    # Get recommendations from the threat data
    recommendations = selected_threat.get("recommendations", [])
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            st.markdown(f"✅ {rec}")
    else:
        st.info("No specific recommendations available for this threat.")

