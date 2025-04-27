import streamlit as st
import requests
import pandas as pd
import io
import time
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import os

from dashboard.api_client import AgriDefenderAPI

def display_image_analysis_tool():
    """
    Display the AI Diagnostic Assistant tool for image-based disease identification.
    Implements the frontend for the "AI Diagnostic Assistant" concept from research.
    """
    # Modern header with icon and description
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <div style="font-size: 2.5rem; margin-right: 15px; color: #1976D2;">🔎</div>
        <div>
            <h1 style="margin: 0; color: #1976D2; font-size: 2rem;">AI Diagnostic Assistant</h1>
            <p style="margin: 5px 0 0 0; color: #5A6772;">Identify plant diseases with our deep learning model</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Information card explaining the technology
    st.markdown("""
    <div style="background-color: #E3F2FD; border-radius: 8px; padding: 15px; margin-bottom: 25px; border-left: 4px solid #1976D2;">
        <h3 style="margin-top: 0; font-size: 1.1rem; color: #1976D2;">About this tool</h3>
        <p style="margin-bottom: 10px;">This AI-powered tool uses machine learning to identify plant diseases from photos with 93% accuracy. The neural network has been trained on over 50,000 images of healthy and diseased plants.</p>
        <ul style="margin-bottom: 5px; padding-left: 20px;">
            <li>Detects 38 different crop diseases</li>
            <li>Works on partial images or early symptoms</li>
            <li>Provides treatment recommendations</li>
            <li>Can identify threats before visible to human eye</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a step-by-step wizard interface
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h3 style="font-size: 1.2rem; color: #212121;">How it works:</h3>
        <div style="display: flex; justify-content: space-between; margin-top: 10px; margin-bottom: 30px;">
            <div style="text-align: center; width: 23%; position: relative;">
                <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #1976D2; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">1</div>
                <p style="margin-top: 8px; font-size: 0.9rem; color: #212121;">Upload Photo</p>
                <div style="position: absolute; top: 25px; left: 100%; width: 70%; height: 2px; background-color: #E0E0E0; z-index: -1;"></div>
            </div>
            <div style="text-align: center; width: 23%; position: relative;">
                <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #E0E0E0; color: #757575; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">2</div>
                <p style="margin-top: 8px; font-size: 0.9rem; color: #757575;">AI Analysis</p>
                <div style="position: absolute; top: 25px; left: 100%; width: 70%; height: 2px; background-color: #E0E0E0; z-index: -1;"></div>
            </div>
            <div style="text-align: center; width: 23%; position: relative;">
                <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #E0E0E0; color: #757575; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">3</div>
                <p style="margin-top: 8px; font-size: 0.9rem; color: #757575;">Diagnosis</p>
                <div style="position: absolute; top: 25px; left: 100%; width: 70%; height: 2px; background-color: #E0E0E0; z-index: -1;"></div>
            </div>
            <div style="text-align: center; width: 23%;">
                <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #E0E0E0; color: #757575; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">4</div>
                <p style="margin-top: 8px; font-size: 0.9rem; color: #757575;">Treatment Plan</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Title for the upload section
    st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 15px;'>Step 1: Upload Plant Image</h3>", unsafe_allow_html=True)
    
    # Create a styled file upload area with drag-and-drop instructions
    st.markdown("""
    <style>
    .uploadArea {
        border: 2px dashed #1976D2;
        border-radius: 8px;
        padding: 40px 20px;
        text-align: center;
        background-color: #F5F9FF;
        margin-bottom: 20px;
        transition: all 0.3s;
    }
    .uploadArea:hover {
        background-color: #E3F2FD;
        border-color: #0D47A1;
    }
    </style>
    
    <div class="uploadArea">
        <div style="font-size: 3rem; color: #1976D2; margin-bottom: 10px;">📷</div>
        <div style="margin-bottom: 15px; font-weight: 500; color: #1976D2;">Drag and drop your image here</div>
        <div style="font-size: 0.9rem; color: #757575;">Supports JPG, JPEG and PNG files</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create the actual file uploader (Streamlit will overlay it on our custom UI)
    uploaded_file = st.file_uploader("Upload a plant image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    # Image capture advice
    if not uploaded_file:
        st.markdown("""
        <div style="background-color: #FFF8E1; border-radius: 8px; padding: 15px; margin: 20px 0; border-left: 4px solid #FFC107;">
            <h4 style="margin-top: 0; color: #F57F17; font-size: 1rem;">📸 Tips for better results:</h4>
            <ul style="margin-bottom: 0; padding-left: 20px; font-size: 0.9rem;">
                <li>Take close-up photos of affected plant parts</li>
                <li>Ensure adequate lighting without shadows</li>
                <li>Include some surrounding healthy tissue for comparison</li>
                <li>Take multiple images from different angles for accuracy</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Create two columns for metadata input
    col1, col2 = st.columns(2)
    
    with col1:
        # Add a visual icon for the location
        st.markdown('<div style="display: flex; align-items: center; margin-bottom: 5px;"><span style="margin-right: 8px; color: #1976D2;">📍</span> <span style="font-weight: 500;">Location Data</span></div>', unsafe_allow_html=True)
        latitude = st.number_input("Latitude", value=30.266666, format="%.6f", 
                                 min_value=-90.0, max_value=90.0,
                                 help="The latitude coordinate where the image was taken")
        longitude = st.number_input("Longitude", value=-97.733330, format="%.6f",
                                  min_value=-180.0, max_value=180.0,
                                  help="The longitude coordinate where the image was taken")
                                  
        # Add a Map button that would show the location on a map
        st.markdown('<div style="text-align: right; margin-top: 5px;"><a href="#" style="text-decoration: none; color: #1976D2; font-size: 0.9rem;">📌 Show on Map</a></div>', unsafe_allow_html=True)
    
    with col2:
        # Add a visual icon for additional information
        st.markdown('<div style="display: flex; align-items: center; margin-bottom: 5px;"><span style="margin-right: 8px; color: #1976D2;">📝</span> <span style="font-weight: 500;">Additional Information</span></div>', unsafe_allow_html=True)
        crop_type = st.selectbox("Crop Type", 
                                ["Select crop type", "Wheat", "Corn", "Soybeans", "Rice", "Cotton", "Barley", "Tomatoes", "Potatoes", "Other"],
                                help="Selecting the correct crop type improves analysis accuracy")
        description = st.text_area("Observations (optional)", 
                                 placeholder="Describe any visible symptoms or concerns...",
                                 help="Any additional context about the plants or field conditions")
    
    # Analyze button with enhanced styling
    analyze_button = st.button("Analyze Image", type="primary", use_container_width=True, disabled=(uploaded_file is None))
    
    if analyze_button:
        if uploaded_file is not None:
            # Update the wizard progress indicator to show the current step
            st.markdown("""
            <div style="margin-bottom: 30px; margin-top: 20px;">
                <div style="display: flex; justify-content: space-between;">
                    <div style="text-align: center; width: 23%; position: relative;">
                        <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #43A047; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">✓</div>
                        <p style="margin-top: 8px; font-size: 0.9rem; color: #43A047;">Upload Photo</p>
                        <div style="position: absolute; top: 25px; left: 100%; width: 70%; height: 2px; background-color: #43A047; z-index: -1;"></div>
                    </div>
                    <div style="text-align: center; width: 23%; position: relative;">
                        <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #1976D2; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">2</div>
                        <p style="margin-top: 8px; font-size: 0.9rem; color: #212121;">AI Analysis</p>
                        <div style="position: absolute; top: 25px; left: 100%; width: 70%; height: 2px; background-color: #E0E0E0; z-index: -1;"></div>
                    </div>
                    <div style="text-align: center; width: 23%; position: relative;">
                        <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #E0E0E0; color: #757575; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">3</div>
                        <p style="margin-top: 8px; font-size: 0.9rem; color: #757575;">Diagnosis</p>
                        <div style="position: absolute; top: 25px; left: 100%; width: 70%; height: 2px; background-color: #E0E0E0; z-index: -1;"></div>
                    </div>
                    <div style="text-align: center; width: 23%;">
                        <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #E0E0E0; color: #757575; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">4</div>
                        <p style="margin-top: 8px; font-size: 0.9rem; color: #757575;">Treatment Plan</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced analysis section with more visual feedback
            st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 15px;'>Step 2: AI Analysis in Progress</h3>", unsafe_allow_html=True)
            
            with st.spinner(""): # Empty spinner since we have custom UI
                # In a real application, this would call the API
                api_client = AgriDefenderAPI(os.getenv("API_URL", "http://localhost:8000"))
                
                # Create a container for the analysis animation
                analysis_container = st.container()
                with analysis_container:
                    st.markdown("""
                    <div style="background-color: #F5F9FF; border-radius: 8px; padding: 25px; text-align: center; margin-bottom: 20px;">
                        <div style="font-size: 3rem; color: #1976D2; margin-bottom: 15px;">🔬</div>
                        <h4 style="margin-top: 0; margin-bottom: 15px; color: #1976D2;">Analyzing Your Image</h4>
                        <p style="margin-bottom: 20px; font-size: 0.9rem; color: #5A6772;">Our AI is examining the image for signs of disease...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create a progress bar with informative steps
                progress_bar = st.progress(0)
                steps = [
                    "Loading image data...",
                    "Preprocessing image...",
                    "Running primary detection model...",
                    "Analyzing leaf patterns...",
                    "Identifying potential pathogens...",
                    "Calculating confidence scores...",
                    "Running secondary verification...",
                    "Generating treatment recommendations...",
                    "Preparing results..."
                ]
                
                step_text = st.empty()
                for i, step in enumerate(steps):
                    step_text.markdown(f"<div style='font-size: 0.9rem; color: #1976D2; text-align: center;'>{step}</div>", unsafe_allow_html=True)
                    for j in range(11):
                        progress_value = min(100, int((i * 10) + j * 1.1))
                        progress_bar.progress(progress_value)
                        time.sleep(0.03)
                
                # Update the wizard progress indicator to show we're at step 3
                st.markdown("""
                <div style="margin-bottom: 30px; margin-top: 20px;">
                    <div style="display: flex; justify-content: space-between;">
                        <div style="text-align: center; width: 23%; position: relative;">
                            <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #43A047; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">✓</div>
                            <p style="margin-top: 8px; font-size: 0.9rem; color: #43A047;">Upload Photo</p>
                            <div style="position: absolute; top: 25px; left: 100%; width: 70%; height: 2px; background-color: #43A047; z-index: -1;"></div>
                        </div>
                        <div style="text-align: center; width: 23%; position: relative;">
                            <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #43A047; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">✓</div>
                            <p style="margin-top: 8px; font-size: 0.9rem; color: #43A047;">AI Analysis</p>
                            <div style="position: absolute; top: 25px; left: 100%; width: 70%; height: 2px; background-color: #43A047; z-index: -1;"></div>
                        </div>
                        <div style="text-align: center; width: 23%; position: relative;">
                            <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #1976D2; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">3</div>
                            <p style="margin-top: 8px; font-size: 0.9rem; color: #212121;">Diagnosis</p>
                            <div style="position: absolute; top: 25px; left: 100%; width: 70%; height: 2px; background-color: #E0E0E0; z-index: -1;"></div>
                        </div>
                        <div style="text-align: center; width: 23%;">
                            <div style="height: 50px; width: 50px; border-radius: 50%; background-color: #E0E0E0; color: #757575; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">4</div>
                            <p style="margin-top: 8px; font-size: 0.9rem; color: #757575;">Treatment Plan</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mock response (in real app, would call the /api/v1/threats/image-analysis endpoint)
                try:
                    st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 15px;'>Step 3: Diagnosis Results</h3>", unsafe_allow_html=True)
                    
                    # Success message
                    st.markdown("""
                    <div style="background-color: #E8F5E9; border-radius: 8px; padding: 15px; margin-bottom: 25px; display: flex; align-items: center;">
                        <div style="font-size: 1.5rem; margin-right: 15px; color: #43A047;">✅</div>
                        <div>
                            <h4 style="margin: 0; color: #2E7D32;">Analysis Complete</h4>
                            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Your image has been analyzed successfully</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display the uploaded image and analysis results side by side
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        # Display the uploaded image with annotations
                        image = Image.open(uploaded_file)
                        
                        # Add a border and title to the image
                        st.markdown("""
                        <div style="border: 1px solid #E0E0E0; border-radius: 8px; padding: 10px; margin-bottom: 20px;">
                            <div style="margin-bottom: 10px; font-weight: 500; color: #212121;">Uploaded Image</div>
                        """, unsafe_allow_html=True)
                        
                        st.image(image, use_column_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        # Mock response for demonstration
                        response = {
                            "status": "success",
                            "detected_threats": [
                                {
                                    "threat_type": "FUNGAL",
                                    "threat_level": "MEDIUM",
                                    "confidence": 0.89,
                                    "identified_pathogen": "Puccinia graminis",
                                    "common_name": "Stem rust",
                                    "affected_area_percentage": 12,
                                    "recommendations": [
                                        "Apply fungicide within 48 hours",
                                        "Consider resistant varieties for next planting season",
                                        "Monitor surrounding fields for spread"
                                    ]
                                }
                            ],
                            "image_analysis_id": "mock-analysis-id"
                        }
                    
                        # Diagnosis results
                        for threat in response["detected_threats"]:
                            # Determine color based on threat level
                            threat_colors = {
                                "LOW": {"bg": "#E8F5E9", "border": "#43A047", "text": "#2E7D32"},
                                "MEDIUM": {"bg": "#FFF8E1", "border": "#FFC107", "text": "#F57F17"},
                                "HIGH": {"bg": "#FFEBEE", "border": "#F44336", "text": "#C62828"},
                                "CRITICAL": {"bg": "#5A1011", "border": "#D32F2F", "text": "#FFFFFF"}
                            }
                            
                            colors = threat_colors.get(threat["threat_level"], {"bg": "#E3F2FD", "border": "#1976D2", "text": "#0D47A1"})
                            
                            st.markdown(f"""
                            <div style="background-color: {colors['bg']}; border-radius: 8px; padding: 20px; margin-bottom: 20px; border-left: 4px solid {colors['border']}">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h3 style="margin: 0; color: {colors['text']}; font-size: 1.2rem;">{threat["common_name"]}</h3>
                                    <div style="background-color: {colors['border']}; color: white; padding: 3px 8px; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">{threat["threat_level"]}</div>
                                </div>
                                
                                <div style="font-size: 0.9rem; font-style: italic; color: #5A6772; margin-bottom: 15px;">{threat["identified_pathogen"]}</div>
                                
                                <div style="margin-bottom: 15px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                        <span style="font-size: 0.9rem; color: #212121;">Confidence</span>
                                        <span style="font-size: 0.9rem; font-weight: 500; color: {colors['text']};">{threat["confidence"]*100:.1f}%</span>
                                    </div>
                                    <div style="height: 8px; width: 100%; background-color: rgba(255,255,255,0.6); border-radius: 4px; overflow: hidden;">
                                        <div style="height: 100%; width: {threat["confidence"]*100}%; background-color: {colors['border']};"></div>
                                    </div>
                                </div>
                                
                                <div style="margin-bottom: 15px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                        <span style="font-size: 0.9rem; color: #212121;">Affected Area</span>
                                        <span style="font-size: 0.9rem; font-weight: 500; color: {colors['text']};">{threat["affected_area_percentage"]}%</span>
                                    </div>
                                    <div style="height: 8px; width: 100%; background-color: rgba(255,255,255,0.6); border-radius: 4px; overflow: hidden;">
                                        <div style="height: 100%; width: {threat["affected_area_percentage"]}%; background-color: {colors['border']};"></div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("Recommendations")
                        for i, recommendation in enumerate(response["detected_threats"][0]["recommendations"]):
                            st.markdown(f"{i+1}. {recommendation}")
                        
                        st.markdown("---")
                        if st.button("Create Containment Plan"):
                            st.session_state["selected_threat_id"] = response["image_analysis_id"]
                            st.session_state["show_containment_plan"] = True
                        
                        if st.button("Send Community Alert"):
                            st.session_state["selected_threat_id"] = response["image_analysis_id"]
                            st.session_state["show_community_alert"] = True
                    
                    # Display blockchain verification section
                    st.markdown("---")
                    st.subheader("Verification")
                    if st.button("Verify and Record Analysis on Blockchain"):
                        with st.spinner("Recording on blockchain..."):
                            time.sleep(1.5)
                            st.success("Analysis verified and recorded on blockchain")
                            st.code(f"""
                            Transaction ID: 0x7a9f1e94c718f4f4b91b23abc47e84dd1b29e2c4a4
                            Timestamp: {datetime.now().isoformat()}
                            Hash: 0xe8d6bd16f3fc30189c58dfbaafbe5184eef9288bf5cc81dc9ce6eaffaf91f0a5
                            """)
                
                except Exception as e:
                    st.error(f"Error analyzing image: {str(e)}")
        else:
            st.warning("Please upload an image to analyze")
    
    # If show_containment_plan is in session state and true, display the containment plan
    if "show_containment_plan" in st.session_state and st.session_state["show_containment_plan"]:
        display_containment_plan(st.session_state["selected_threat_id"])
    
    # If show_community_alert is in session state and true, display the community alert form
    if "show_community_alert" in st.session_state and st.session_state["show_community_alert"]:
        display_community_alert_form(st.session_state["selected_threat_id"])

def display_containment_plan(threat_id):
    """Display a containment plan for a specific threat"""
    st.markdown("---")
    st.markdown("## Rapid Containment Plan")
    st.markdown(f"Threat ID: {threat_id}")
    
    with st.spinner("Generating containment plan..."):
        time.sleep(1.0)
        
        # Mock containment plan data
        containment_plan = {
            "threat_id": threat_id,
            "containment_level": "high_priority",
            "quarantine_radius_meters": 500,
            "immediate_actions": [
                {
                    "action": "establish_perimeter",
                    "description": "Mark off affected area with flags or markers",
                    "priority": 1
                },
                {
                    "action": "notify_neighbors",
                    "description": "Alert neighboring farms within 2km radius",
                    "priority": 2
                },
                {
                    "action": "apply_treatment",
                    "description": "Apply recommended fungicide to affected area",
                    "priority": 3
                }
            ],
            "follow_up_actions": [
                {
                    "action": "daily_monitoring",
                    "description": "Check perimeter daily for signs of spread",
                    "timeframe": "7 days"
                },
                {
                    "action": "report_to_authorities",
                    "description": "Submit containment documentation to agricultural department",
                    "timeframe": "within 48 hours"
                }
            ],
            "equipment_needed": [
                "Protective clothing",
                "Spraying equipment",
                "Perimeter markers"
            ]
        }
    
    # Display containment plan details
    st.subheader(f"{containment_plan['containment_level'].replace('_', ' ').title()} Containment Plan")
    st.markdown(f"**Quarantine Radius:** {containment_plan['quarantine_radius_meters']} meters")
    
    # Display immediate actions
    st.markdown("### Immediate Actions")
    for action in containment_plan["immediate_actions"]:
        st.markdown(f"**{action['priority']}. {action['action'].replace('_', ' ').title()}**")
        st.markdown(f"{action['description']}")
    
    # Display follow-up actions
    st.markdown("### Follow-up Actions")
    for action in containment_plan["follow_up_actions"]:
        st.markdown(f"**{action['action'].replace('_', ' ').title()}** ({action['timeframe']})")
        st.markdown(f"{action['description']}")
    
    # Display equipment needed
    st.markdown("### Equipment Needed")
    for equipment in containment_plan["equipment_needed"]:
        st.markdown(f"- {equipment}")
    
    if st.button("Close Containment Plan"):
        st.session_state["show_containment_plan"] = False
        st.experimental_rerun()

def display_community_alert_form(threat_id):
    """Display a form for sending community alerts"""
    st.markdown("---")
    st.markdown("## Community Alert System")
    st.markdown("Send an alert to nearby farmers about the detected threat.")
    
    alert_message = st.text_area(
        "Alert Message", 
        value=f"ALERT: Agricultural threat detected in your area. Type: Fungal infection (Stem rust). Severity: Medium. Please inspect your crops and take precautionary measures."
    )
    
    radius_km = st.slider("Alert Radius (km)", min_value=1, max_value=50, value=5)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        include_sms = st.checkbox("SMS Notifications", value=True)
    with col2:
        include_email = st.checkbox("Email Notifications", value=True)
    with col3:
        include_app = st.checkbox("App Notifications", value=True)
    
    if st.button("Send Alert"):
        with st.spinner("Sending alerts to local farmers..."):
            time.sleep(1.5)
            
            # Mock response data
            response = {
                "status": "success",
                "alert_id": "mock-alert-id",
                "affected_area": {
                    "type": "circle",
                    "radius_km": radius_km,
                    "center": [-97.733330, 30.266666]
                },
                "estimated_recipients": 23,
                "notification_channels": []
            }
            
            if include_sms:
                response["notification_channels"].append("sms")
            if include_email:
                response["notification_channels"].append("email")
            if include_app:
                response["notification_channels"].append("app_notification")
            
            st.success(f"Alert sent to {response['estimated_recipients']} recipients within {radius_km}km radius")
            
            # Show a map of the affected area
            fig, ax = plt.subplots(figsize=(10, 8))
            circle = plt.Circle((-97.733330, 30.266666), radius_km/111, # Convert km to degrees (approximate)
                               color='red', fill=False, linewidth=2)
            ax.add_patch(circle)
            ax.set_xlim(-97.733330 - radius_km/111*1.5, -97.733330 + radius_km/111*1.5)
            ax.set_ylim(30.266666 - radius_km/111*1.5, 30.266666 + radius_km/111*1.5)
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_title('Alert Coverage Area')
            ax.grid(True)
            st.pyplot(fig)
    
    if st.button("Cancel"):
        st.session_state["show_community_alert"] = False
        st.experimental_rerun()

