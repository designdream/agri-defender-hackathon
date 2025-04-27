import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from dashboard.api_client import AgriDefenderAPI

def display_companion_planting_optimizer():
    """
    Display the companion planting optimizer tool.
    Implements the frontend for the "Companion Planting Optimizer" concept from research.
    """
    st.markdown("## Companion Planting Optimizer")
    st.markdown("""
    Optimize your planting strategy to naturally suppress pests and diseases. 
    This tool recommends companion plants that work together to create a more resilient field ecosystem.
    """)
    
    # Create form for user input
    with st.form("companion_planting_form"):
        # Crop selection
        crop_options = ["Corn", "Wheat", "Soybeans", "Cotton", "Rice", "Tomatoes", "Potatoes", "Lettuce"]
        crop_type = st.selectbox("Main Crop", options=crop_options)
        
        # Threat type selection
        threat_options = ["FUNGAL", "BACTERIAL", "VIRAL", "PEST", "ANY"]
        threat_type = st.selectbox("Target Threat Type", options=threat_options)
        
        # Location input
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=30.266666, format="%.6f", 
                                      min_value=-90.0, max_value=90.0)
        with col2:
            longitude = st.number_input("Longitude", value=-97.733330, format="%.6f",
                                       min_value=-180.0, max_value=180.0)
        
        # Submit button
        submit_button = st.form_submit_button("Generate Recommendations")
    
    # Process form submission
    if submit_button:
        with st.spinner("Analyzing optimal companion plants..."):
            # In a real app, this would call the API client
            api_client = AgriDefenderAPI(os.getenv("API_URL", "http://localhost:8000"))
            
            # Create a progress bar for visual feedback
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Mock response (in a real app, would call the /api/v1/threats/companion-plants endpoint)
            response = {
                "main_crop": crop_type,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "hardiness_zone": "8b",
                    "soil_type": "clay loam"
                },
                "companion_recommendations": [
                    {
                        "plant": "Marigold",
                        "benefits": ["Repels nematodes", "Deters many insects"],
                        "planting_pattern": "Border around field",
                        "compatibility_score": 0.95
                    },
                    {
                        "plant": "Basil",
                        "benefits": ["Repels thrips and flies", "Enhances yield"],
                        "planting_pattern": "Interspersed every 10 rows",
                        "compatibility_score": 0.87
                    },
                    {
                        "plant": "Clover",
                        "benefits": ["Fixes nitrogen", "Suppresses weeds"],
                        "planting_pattern": "Cover crop in rotations",
                        "compatibility_score": 0.82
                    }
                ],
                "implementation_notes": "Plant companions at least 2 weeks before main crop for maximum effect",
                "estimated_protection_level": "medium"
            }
            
            # Display results
            st.success(f"Companion plant recommendations for {crop_type} generated successfully")
            
            # Display location info
            st.subheader("Field Information")
            st.markdown(f"""
            **Location:** {response['location']['latitude']}, {response['location']['longitude']}  
            **Hardiness Zone:** {response['location']['hardiness_zone']}  
            **Soil Type:** {response['location']['soil_type']}
            """)
            
            # Display overall protection level
            protection_color = {
                "low": "red",
                "medium": "orange",
                "high": "green"
            }.get(response["estimated_protection_level"], "gray")
            
            st.markdown(f"""
            <div style='background-color: rgba(0, 0, 0, 0.05); padding: 15px; border-radius: 5px;'>
                <h3>Estimated Protection Level: <span style='color: {protection_color};'>{response["estimated_protection_level"].upper()}</span></h3>
                <p>{response["implementation_notes"]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display companion recommendations
            st.subheader("Recommended Companion Plants")
            
            # Create a layout for the recommendations
            cols = st.columns(min(3, len(response["companion_recommendations"])))
            
            for i, companion in enumerate(response["companion_recommendations"]):
                with cols[i % len(cols)]:
                    st.markdown(f"""
                    <div style='background-color: rgba(240, 248, 255, 0.8); padding: 15px; border-radius: 5px; height: 100%;'>
                        <h3 style='text-align: center;'>{companion["plant"]}</h3>
                        <p style='text-align: center;'><strong>Compatibility:</strong> {companion["compatibility_score"]*100:.0f}%</p>
                        <p><strong>Benefits:</strong></p>
                        <ul>
                        {"".join([f"<li>{benefit}</li>" for benefit in companion["benefits"]])}
                        </ul>
                        <p><strong>Planting Pattern:</strong> {companion["planting_pattern"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display planting diagram
            st.subheader("Planting Pattern Visualization")
            
            # Create a simple visualization of the planting pattern
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Set up the plot
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Create a simple field diagram
            # Main crop as background
            rect = plt.Rectangle((0, 0), 10, 10, facecolor='#e6f5e6', edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # Add a title
            ax.set_title(f'Companion Planting Pattern for {crop_type}', fontsize=14)
            
            # Plot different companion plants based on planting pattern
            for companion in response["companion_recommendations"]:
                if "Border" in companion["planting_pattern"]:
                    # Draw a border of companion plants
                    border_width = 0.5
                    outer = plt.Rectangle((0, 0), 10, 10, fill=False, edgecolor='black', linewidth=2)
                    inner = plt.Rectangle((border_width, border_width), 
                                         10 - 2*border_width, 10 - 2*border_width, 
                                         fill=False, edgecolor='black', linewidth=1, linestyle='--')
                    border = plt.Rectangle((0, 0), 10, 10, facecolor='#ffe6cc', edgecolor='black', linewidth=0, alpha=0.4)
                    border2 = plt.Rectangle((border_width, border_width), 
                                           10 - 2*border_width, 10 - 2*border_width, 
                                           facecolor='#e6f5e6', edgecolor='black', linewidth=0)
                    ax.add_patch(border)
                    ax.add_patch(border2)
                    ax.add_patch(outer)
                    ax.add_patch(inner)
                    # Add label
                    ax.text(5, 9.7, companion["plant"], ha='center', va='center', fontsize=10, 
                           bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
                
                elif "Interspersed" in companion["planting_pattern"]:
                    # Draw interspersed companion plants
                    for row in range(1, 10, 2):
                        for col in range(1, 10):
                            circle = plt.Circle((col, row), 0.2, facecolor='#ffb3b3', edgecolor='black', linewidth=1)
                            ax.add_patch(circle)
                    # Add label
                    ax.text(5, 1.3, companion["plant"], ha='center', va='center', fontsize=10,
                           bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
                
                elif "Cover crop" in companion["planting_pattern"]:
                    # Add text note about cover crop
                    ax.text(5, 5, f"{companion['plant']}\n(Cover crop in rotation)", 
                           ha='center', va='center', fontsize=12, fontweight='bold',
                           bbox=dict(facecolor='#e6ccff', alpha=0.4, edgecolor='black', boxstyle='round,pad=0.5'))
            
            # Add a legend
            ax.text(0.5, -0.1, crop_type, transform=ax.transAxes, ha='center', fontsize=12)
            
            # Display the plot
            st.pyplot(fig)
            
            # Display seasonal information
            st.subheader("Seasonal Timing")
            st.markdown("""
            ### Optimal Planting Schedule
            
            | Companion Plant | Plant Before Main Crop | Optimal Time |
            |-----------------|------------------------|--------------|
            | Marigold        | 2-3 weeks before      | Early Spring |
            | Basil           | At same time          | After frost  |
            | Clover          | After harvest         | Fall         |
            
            **Note:** Adjust timing based on your specific climate zone and local growing conditions.
            """)
            
            # Display download button for implementation plan
            st.download_button(
                label="Download Companion Planting Plan",
                data="This would be a PDF or CSV file with the companion planting plan in a real implementation",
                file_name=f"companion_planting_plan_{crop_type.lower()}.pdf",
                mime="application/pdf"
            )
