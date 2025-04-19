"""
Scuba Diving Assistant Web Application

This is the main application file that implements a Streamlit-based web interface for scuba diving tools.
The application provides multiple features including:
- Dive logging and management
- Dive planning with PADI tables
- Travel planning for dive trips
- Weather information for dive sites
- Digital dive journal entries
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import io
import base64
import os
import tempfile
import webbrowser
from dive_log import DiveLog, save_dive_log
from dive_travel import DiveTravelCalculator
from dive_journal import DiveJournal
from dive_table import (
    get_pressure_group,  # Calculate pressure group based on depth/time
    get_new_group_after_surface_interval as get_new_pressure_group,  # Calculate new group after surface interval
    get_rnt,  # Get residual nitrogen time
    check_ndl,  # Check no-decompression limits
    calculate_total_bottom_time,  # Calculate total bottom time including residual nitrogen
    validate_repetitive_dive,  # Validate safety of repetitive dives
    no_deco_limits  # PADI no-decompression limits table
)

# Read and encode the tank image
def get_tank_image_base64():
    image_path = os.path.join(os.path.dirname(__file__), "static", "images", "tank.png")
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

st.set_page_config(
    page_title="Scuba Diving Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
    <style>
    /* New color scheme */
    :root {
        --primary: #0A192F;     /* Dark blue background */
        --secondary: #2A9D8F;   /* Turquoise for buttons */
        --accent: #64FFDA;      /* Light turquoise for highlights */
        --text: #E6F1FF;        /* Light blue text */
        --dark-teal: #1B4B45;   /* Dark teal for selected/active states */
        --black: #000000;       /* Black for sidebar text */
    }
    
    /* Global font and color settings */
    * {
        font-family: 'Courier New', monospace !important;
    }
    
    /* Main content gradient background */
    section[data-testid="stSidebarContent"], div[data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #000000 0%, #002F31 100%) !important;
    }
    
    /* Sidebar styles */
    .css-1d391kg, [data-testid="stSidebar"] {  /* Sidebar background */
        background-color: var(--secondary) !important;
    }
    [data-testid="stSidebar"] * {  /* All sidebar elements */
        color: var(--black) !important;
    }
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] * {
        color: var(--black) !important;
    }
    [data-testid="stSidebar"] button:hover {  /* Sidebar button hover */
        background-color: rgba(0, 0, 0, 0.1) !important;
    }
    /* Force black text in sidebar */
    .css-pkbazv, .css-17lntkn, .css-5rimss, .css-1629p8f {
        color: var(--black) !important;
    }
    
    /* Style radio buttons */
    .stRadio > div {
        color: var(--text);
    }
    .stRadio [role="radiogroup"] {
        gap: 0.5rem !important;
    }
    .stRadio [data-testid="stMarkdownContainer"] {
        margin-bottom: 0.5rem !important;
    }
    .stRadio label {
        padding: 0.25rem !important;
    }
    
    /* Button styles */
    .stButton>button {
        background-color: var(--secondary);
        color: var(--text);
        border-radius: 20px;
    }
    
    /* Input styles */
    h1, h2, h3 {
        color: var(--text);
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: var(--secondary);
        color: var(--text);
        border-radius: 10px;
    }
    .stSelectbox>div>div>div {
        background-color: var(--secondary);
        color: var(--text);
    }
    
    /* Form styles */
    .dive-form {
        border: 2px solid var(--secondary);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
    }
    .section-title {
        color: var(--accent);
        font-size: 1.2em;
        margin-bottom: 10px;
    }
    
    /* Style data display */
    .stDataFrame {
        color: var(--text) !important;
    }
    .stDataFrame td, .stDataFrame th {
        color: var(--text) !important;
        background-color: var(--primary) !important;
    }
    .stDataFrame [data-testid="stTable"] {
        color: var(--text) !important;
    }
    
    /* Style radio buttons and checkboxes */
    .stRadio > div, .stCheckbox > div {
        color: var(--text);
    }
    
    /* Style success/error messages */
    .stSuccess {
        color: var(--accent) !important;
    }
    .stError {
        color: #FF6B6B !important;
    }
    
    /* Style time and date inputs */
    .stDateInput > div > div {
        color: var(--text) !important;
        background-color: var(--secondary) !important;
    }
    
    /* Style sliders */
    .stSlider {
        color: var(--text) !important;
    }
    .stSlider .stSlideHandle {
        background-color: var(--accent) !important;
    }
    
    /* Hide all empty containers */
    div:empty,
    [data-testid="stHorizontalBlock"] div:empty,
    [data-testid="stVerticalBlock"] div:empty,
    .element-container:empty {
        display: none !important;
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        border: none !important;
        background: none !important;
    }
    
    /* Style all text elements */
    div, p, span, label, td, th, input, select, button {
        font-family: 'Courier New', monospace !important;
        color: var(--text);
    }
    
    /* Style links */
    a, a:visited {
        color: var(--text) !important;
        text-decoration: none !important;
    }
    
    a:hover, a:active {
        color: var(--primary) !important;
    }
    
    /* Fix table styles */
    table {
        color: var(--text) !important;
        background-color: var(--primary) !important;
    }
    thead tr th {
        background-color: var(--secondary) !important;
        color: var(--text) !important;
    }
    tbody tr:nth-child(odd) {
        background-color: rgba(42, 157, 143, 0.1) !important;
    }
    tbody tr:nth-child(even) {
        background-color: rgba(42, 157, 143, 0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

def load_dive_logs():
    try:
        with open("dive_logs.json", "r") as f:
            logs = json.load(f)
        return logs
    except FileNotFoundError:
        return []

def dive_log_page():
    st.title(" Log New Dive")

    # Add custom CSS for input styling
    st.markdown("""
        <style>
        .stTextInput, .stNumberInput {
            font-family: 'Courier New', monospace;
        }
        div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label {
            color: var(--text) !important;
            font-size: 1.1em !important;
        }
        /* Hide empty boxes */
        [data-baseweb="input"] {
            background-color: transparent !important;
            border-color: transparent !important;
        }
        [data-baseweb="input"]:focus {
            background-color: rgba(42, 157, 143, 0.2) !important;
            border-color: #64FFDA !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header section with diver name prominently displayed
    st.subheader("Diver Information")
    diver_name = st.text_input("Diver Name", placeholder="Enter your full name")
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    
    # Rest of the form
    st.subheader("Dive Details")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        dive_number = st.number_input("Dive #", min_value=1, value=1)
    with col2:
        date = st.date_input("Date")
    with col3:
        location = st.text_input("Location")
    
    # Create three main columns for the form
    left_col, middle_col, right_col = st.columns([2, 1, 1])
    
    with left_col:
        st.markdown('<div class="dive-form">', unsafe_allow_html=True)
        # Depth and Time section
        st.markdown('<div class="section-title">Depth & Time</div>', unsafe_allow_html=True)
        depth_avg = st.number_input("Average Depth (ft)", min_value=0.0)
        depth_max = st.number_input("Maximum Depth (ft)", min_value=0.0)
        bottom_time = st.slider("Bottom Time (minutes)", min_value=0, max_value=120, value=30, step=5)
        safety_stop = st.slider("Safety Stop Time (minutes)", min_value=0, max_value=10, value=3, step=1)
        col1, col2, col3 = st.columns(3)
        with col1:
            rnt = st.number_input("RNT", min_value=0)
        with col2:
            abt = st.number_input("ABT", min_value=0)
        with col3:
            tbt = rnt + abt
            st.metric("TBT", f"{tbt} min")
        
        # Environment type selection
        st.subheader("Environment")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Water Type")
            fresh = st.checkbox("Fresh")
            salt = st.checkbox("Salt")
            deep = st.checkbox("Deep")
        
        with col2:
            st.write("Entry Type")
            shore = st.checkbox("Shore")
            boat = st.checkbox("Boat")
            night = st.checkbox("Night")
        
        # Build the dive_type list from selections
        dive_type = []
        if fresh: dive_type.append("Fresh")
        if salt: dive_type.append("Salt")
        if deep: dive_type.append("Deep")
        if shore: dive_type.append("Shore")
        if boat: dive_type.append("Boat")
        if night: dive_type.append("Night")
        
        # Activities
        st.subheader("Activities")
        activities = st.multiselect("Select Activities", 
            ["Recreation", "Wreck", "Reef", "Navigation", "Cave", "Search & Recovery", "Photography"],
            default=None,
            placeholder="Choose activities..."
        )
    
    with middle_col:
        st.markdown('<div class="dive-form">', unsafe_allow_html=True)
        # Temperature
        st.markdown('<div class="section-title">Temperature</div>', unsafe_allow_html=True)
        temp_air = st.slider("Air Temperature (°F)", min_value=32, max_value=120, value=75)
        temp_surface = st.slider("Surface Temperature (°F)", min_value=32, max_value=95, value=75)
        temp_bottom = st.slider("Bottom Temperature (°F)", min_value=32, max_value=95, value=70)
        
        # Visibility
        st.markdown('<div class="section-title">Visibility</div>', unsafe_allow_html=True)
        visibility = st.number_input("Distance (ft)")
        
        # Air
        st.markdown('<div class="section-title">Air</div>', unsafe_allow_html=True)
        air_start = st.number_input("Start (psi)")
        air_end = st.number_input("End (psi)")
        gas_type = st.radio("Gas Type", ["Air", "Nitrox"])
        if gas_type == "Nitrox":
            nitrox_percent = st.number_input("Nitrox %", min_value=21, max_value=40)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with right_col:
        st.markdown('<div class="dive-form">', unsafe_allow_html=True)
        # Weight
        st.markdown('<div class="section-title">Weight</div>', unsafe_allow_html=True)
        weight = st.number_input("Weight (lbs)")
        
        weight_adj_type = st.radio("", ["⚖️", "➕", "➖"], horizontal=True, key="weight_adj_type", label_visibility="collapsed")
        if weight_adj_type in ["➕", "➖"]:
            weight_change = st.number_input("Change Amount (lbs)", min_value=0.0, value=0.0, step=0.5)
            if weight_adj_type == "➕":
                st.info(f"New weight will be: {weight + weight_change} lbs")
            else:
                st.info(f"New weight will be: {weight - weight_change} lbs")
        
        # Exposure Protection
        st.markdown('<div class="section-title">Exposure Protection</div>', unsafe_allow_html=True)
        protection = {}
        for item in ["Full", "Shorty", "Boots", "Hood", "Gloves"]:
            col1, col2 = st.columns([2, 1])
            with col1:
                use_item = st.checkbox(item)
            with col2:
                if use_item:
                    protection[item] = st.number_input(f"{item} (mm)", key=f"protection_{item}")
        
        # Equipment
        st.markdown('<div class="section-title">Equipment</div>', unsafe_allow_html=True)
        camera = st.checkbox("Camera")
        computer = st.checkbox("Computer")
        flashlight = st.checkbox("Flashlight")
        
        # Verification
        st.markdown('<div class="section-title">Verification</div>', unsafe_allow_html=True)
        ver_type = st.selectbox("Type", ["Instructor", "Divemaster", "Buddy"], key="ver_type")
        cert_num = st.text_input("Certification #")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Save button
    if st.button("Save Dive Log", use_container_width=True):
        equipment = []
        if camera: equipment.append("Camera")
        if computer: equipment.append("Computer")
        if flashlight: equipment.append("Flashlight")
        
        dive_log = DiveLog(
            diver_name=diver_name,
            dive_number=dive_number,
            date=date.strftime("%Y-%m-%d"),
            location=location,
            depth_avg=depth_avg,
            depth_max=depth_max,
            bottom_time=bottom_time,
            safety_stop_time=safety_stop,
            rnt=rnt,
            abt=abt,
            tbt=tbt,
            dive_type=dive_type,
            activities=activities,
            temperature_air=temp_air,
            temperature_surface=temp_surface,
            temperature_bottom=temp_bottom,
            visibility_ft=visibility,
            air_start_psi=air_start,
            air_end_psi=air_end,
            gas_type=gas_type,
            weight_lbs=weight,
            weight_adjustment=weight_adj_type,
            exposure_protection=protection,
            equipment_used=equipment,
            verification_type=ver_type,
            certification_number=cert_num,
            nitrox_percentage=nitrox_percent if gas_type == "Nitrox" else None
        )
        save_dive_log(dive_log)
        st.success("Dive log saved successfully!")

def view_logs_page():
    st.title(" View Dive Logs")
    
    # Load dive logs
    df = pd.DataFrame(load_dive_logs())
    
    if df.empty:
        st.warning("No dive logs found. Enter a dive log to view here.")
        return
    
    # Create visualization
    fig = px.scatter(df, x='date', y='depth_max', 
                    title='Maximum Depth Over Time',
                    labels={'date': 'Date', 'depth_max': 'Maximum Depth (ft)'},
                    color_discrete_sequence=['#64FFDA'])  # Light turquoise for points
    
    fig.update_traces(marker=dict(
        size=12,
        line=dict(color='#2A9D8F', width=2)  # Teal outline
    ))
    
    # Update layout for rounded corners and styling
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(14,17,23,0.5)',  # Semi-transparent dark background
        title=dict(
            text='Maximum Depth Over Time',
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=24)
        ),
        margin=dict(t=70, l=50, r=30, b=50),  # Increased top margin for title
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(42,157,143,0.1)',
            showline=True,
            linewidth=2,
            linecolor='#2A9D8F'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(42,157,143,0.1)',
            showline=True,
            linewidth=2,
            linecolor='#2A9D8F'
        )
    )
    
    # Add custom CSS for rounded corners
    st.markdown("""
        <style>
        .js-plotly-plot .plotly, .js-plotly-plot .plot-container {
            border-radius: 15px !important;
            overflow: hidden !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display the graph
    st.plotly_chart(fig, use_container_width=True)
    
    # Prepare data for download
    # Reorder columns to show diver_name first
    columns = ['diver_name', 'dive_number', 'date', 'location'] + [col for col in df.columns if col not in ['diver_name', 'dive_number', 'date', 'location', 'id', 'created_at']]
    df = df[columns]
    
    # Add custom download button CSS
    st.markdown("""
        <style>
        /* Make all links white */
        .download-section a {
            color: var(--text) !important;
            text-decoration: none !important;
        }
        
        .download-section a:hover {
            color: var(--primary) !important;
        }
        
        .download-button {
            background-color: var(--secondary);
            color: var(--text);
            padding: 0.75rem 1.5rem;
            border-radius: 20px;
            border: none;
            font-family: 'Courier New', monospace !important;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: block;
            text-align: center;
            text-decoration: none;
            margin: 1rem auto;
            width: fit-content;
            min-width: 300px;
        }
        
        .download-button:hover {
            background-color: var(--accent);
            color: var(--primary) !important;
        }
        
        .download-section {
            text-align: center;
            padding: 1rem;
            margin: 2rem 0;
            border: 2px solid var(--secondary);
            border-radius: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create download section
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    
    # Convert dataframe to CSV
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    
    # Create download link with custom styling
    href = f'<a href="data:file/csv;base64,{b64}" download="dive_logs.csv" class="download-button"> Download Dive Logs CSV </a>'
    st.markdown(href, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def dive_planner_page():
    st.title(" PADI Dive Planner")
    
    # Get available depths from the dive tables
    available_depths = sorted(list(no_deco_limits.keys()))
    
    # First Dive
    st.header('First Dive')
    col1, col2 = st.columns(2)
    
    with col1:
        depth1 = st.selectbox(
            'First Dive Depth (ft)',
            available_depths,
            format_func=lambda x: f'{x} ft'
        )
    
    with col2:
        time1 = st.slider(
            'First Dive Bottom Time (minutes)',
            min_value=1,
            max_value=200,
            value=40
        )
    
    pg1 = get_pressure_group(depth1, time1)
    st.markdown(f"""
        <div class="info-box">
            <p class="info-text">Pressure Group after first dive: {pg1}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Surface Interval
    st.header('Surface Interval')
    interval = st.slider(
        'Surface Interval (minutes)',
        min_value=10,
        max_value=240,
        value=60
    )
    
    pg2 = get_new_pressure_group(pg1, interval)
    st.markdown(f"""
        <div class="info-box">
            <p class="info-text">New Pressure Group after surface interval: {pg2}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Second Dive
    st.header('Second Dive')
    col3, col4 = st.columns(2)
    
    with col3:
        depth2 = st.selectbox(
            'Second Dive Depth (ft)',
            available_depths,
            format_func=lambda x: f"{x} ft"
        )
    
    with col4:
        time2 = st.slider(
            'Second Dive Planned Bottom Time (minutes)',
            min_value=1,
            max_value=200,
            value=40
        )
    
    rnt = get_rnt(pg2, depth2)
    tbt = rnt + time2
    
    st.write(f"Residual Nitrogen Time: {rnt} min")
    st.write(f"Total Bottom Time: {tbt} min")
    
    if check_ndl(depth2, tbt):
        st.success("Second dive is within no-decompression limits.")
    else:
        st.error(" WARNING: Second dive exceeds no-decompression limits!")

    # Add explanations
    st.markdown("""
    ---
    ### Residual Nitrogen Time (RNT)
    Residual Nitrogen Time represents the amount of nitrogen remaining in your body from your previous dive. Think of it as:
    - The number of minutes you're considered to have already spent at your new depth
    - Based on your pressure group (A-Z) and your planned depth
    - Higher pressure groups and deeper depths mean higher RNT
    - After a long surface interval, your pressure group drops, leading to lower RNT
    
    For example: If your RNT is 17 minutes, it means your body already has the same amount of nitrogen as if you had already been at your planned depth for 17 minutes.

    ---
    ### Total Bottom Time
    For a repetitive dive (second dive), the total bottom time is calculated as:
    - **Residual Nitrogen Time (RNT)** + **Planned Bottom Time**
    
    This is NOT the first dive time + second dive time. Here's why:
    1. Surface interval reduces your nitrogen load (changes your pressure group)
    2. RNT represents how much "equivalent bottom time" you start with
    3. Total bottom time = RNT + planned time for the second dive
    """)
    
    # Add PADI table download button
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; margin-top: 2rem;'>
            <a href='https://www.a1scubadiving.com/wp-content/uploads/2018/06/PADI-Recreational-Dive-Table-Planner.pdf' 
               target='_blank' 
               style='
                   background-color: #2A9D8F;
                   color: white;
                   padding: 0.5rem 1rem;
                   text-decoration: none;
                   border-radius: 5px;
                   font-family: "Courier New", monospace;
                   transition: background-color 0.3s;
                   display: inline-block;
                   margin: 1rem 0;
               '
               onmouseover='this.style.backgroundColor="#64FFDA"'
               onmouseout='this.style.backgroundColor="#2A9D8F"'>
                View PADI Dive Tables
            </a>
        </div>
    """, unsafe_allow_html=True)

def travel_planner_page():
    st.title(" Dive Travel Planner")
    
    st.markdown('<div class="dive-form">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Flight Details</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        flight_date = st.date_input("Flight Date")
    with col2:
        flight_time = st.time_input("Flight Time")
    
    st.markdown('<div class="section-title">Last Dive</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        last_dive_date = st.date_input("Last Dive Date")
    with col4:
        last_dive_time = st.time_input("Last Dive Time")
    
    # Common diving depths
    depths = [10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
    last_dive_depth = st.selectbox(
        "Last Dive Depth",
        depths,
        format_func=lambda x: f"{x} ft"
    )
    
    last_dive_duration = st.slider("Last Dive Duration (minutes)", min_value=0, max_value=200, value=30, step=5)
    repetitive_dives = st.checkbox("Multiple dives within 24 hours")
    
    if st.button("Check Safety", use_container_width=True):
        calculator = DiveTravelCalculator()
        last_dive = datetime.combine(last_dive_date, last_dive_time)
        flight_datetime = datetime.combine(flight_date, flight_time)
        
        is_safe, message = calculator.is_safe_to_fly(last_dive, flight_datetime, "DAN", repetitive_dives)
        
        if is_safe:
            st.success(message)
        else:
            st.error(message)
            st.warning("""
            Flying too soon after diving increases your risk of decompression sickness (DCS).
            Common symptoms include:
            - Joint pain
            - Numbness or tingling
            - Dizziness
            - Difficulty breathing
            
            Please follow the recommended surface interval guidelines for your safety.
            Consider rebooking your flight if possible.
            """)
    st.markdown('</div>', unsafe_allow_html=True)

def weather_page():
    st.title(" Weather & Conditions")
    
    # Create a container for the map that takes up most of the screen
    map_container = st.container()
    
    # Create a container for the text that will appear at the bottom
    text_container = st.container()
    
    with map_container:
        st.markdown("""
            ### Interactive Weather Map
            View real-time weather conditions, waves, wind, and water temperature for your dive locations.
            Data provided by Windy.com
        """)
        
        # Set the map to be very tall
        st.markdown("""
            <style>
            iframe {
                width: 100%;
                min-height: 800px !important;
                border: 2px solid var(--secondary);
                border-radius: 15px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Embed Windy map using HTML iframe
        windy_html = f"""
            <div style="height: 800px;">
                <iframe 
                    src="https://embed.windy.com/embed2.html?lat=25.000&lon=-80.000&zoom=5&level=surface&overlay=wind&menu=&message=&marker=&calendar=&pressure=&type=map&location=coordinates&detail=&detailLat=25.000&detailLon=-80.000&metricWind=default&metricTemp=default&radarRange=-1"
                    style="width: 100%; height: 100%; border: none;">
                </iframe>
            </div>
        """
        st.components.v1.html(windy_html, height=800)
    
    # Add some spacing between map and text
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    with text_container:
        st.markdown("""
            ### Weather Conditions Guide
            
            #### Safe Diving Conditions:
            - Wind Speed: < 15 knots
            - Wave Height: < 3 feet
            - Visibility: > 15 feet
            - Current: < 1 knot
            
            #### Weather Warning Signs:
            - Approaching storm systems
            - Rapidly changing conditions
            - Strong wind shifts
            - Building wave heights
            
            Always check local weather reports and consult with dive operators before diving.
        """)

def journal_entry_page():
    st.title(" Dive Journal")
    
    # Initialize journal
    journal = DiveJournal()
    
    with st.form("journal_entry", clear_on_submit=True):
        st.markdown('<div class="section-title">New Journal Entry</div>', unsafe_allow_html=True)
        
        # Basic dive info
        col1, col2, col3 = st.columns(3)
        with col1:
            dive_date = st.date_input("Dive Date", value=datetime.now())
        with col2:
            dive_location = st.text_input("Dive Location")
        with col3:
            author = st.text_input("Diver Name")
            
        # Journal title and content
        title = st.text_input("Entry Title")
        content = st.text_area("Your Experience", height=200, 
                             help="Write about your dive experience, marine life encounters, conditions, or anything memorable!")
        
        # Photo upload
        uploaded_file = st.file_uploader("Upload a Photo", type=['png', 'jpg', 'jpeg'], 
                                       help="Share a photo from your dive!")
        
        # Mood and rating
        col3, col4 = st.columns(2)
        with col3:
            mood = st.select_slider("Dive Mood", 
                                  options=["", "", "", "", ""],
                                  value="")
        with col4:
            rating = st.slider("Rate this dive", 1, 5, 5)
        
        if st.form_submit_button("Save Journal Entry", use_container_width=True):
            entry = {
                "date": dive_date.isoformat(),
                "location": dive_location,
                "author": author,
                "title": title,
                "content": content,
                "mood": mood,
                "rating": rating
            }
            
            if journal.save_journal(entry, uploaded_file):
                st.success("Journal entry saved successfully! ")
            else:
                st.error("Failed to save journal entry.")

def view_journals_page():
    st.title(" My Dive Journals")
    
    journal = DiveJournal()
    entries = journal.get_all_journals()
    
    if not entries:
        st.info("No journal entries yet. Start writing about your dive experiences!")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        location_filter = st.multiselect(
            "Filter by Location",
            options=sorted(set(e['location'] for e in entries))
        )
    with col2:
        author_filter = st.multiselect(
            "Filter by Diver",
            options=sorted(set(e['author'] for e in entries))
        )
    
    # Apply filters
    filtered_entries = entries
    if location_filter:
        filtered_entries = [e for e in filtered_entries if e['location'] in location_filter]
    if author_filter:
        filtered_entries = [e for e in filtered_entries if e['author'] in author_filter]
    
    # Display entries
    for entry in filtered_entries:
        with st.expander(f"{entry['title']} - {entry['date'][:10]} ({entry['location']})"):
            # Display photo if available
            if entry.get('image_path'):
                st.image(entry['image_path'])
            
            col1, col2, col3, col4 = st.columns([2,1,1,1])
            with col1:
                st.write(f"**Location:** {entry['location']}")
            with col2:
                st.write(f"**Author:** {entry['author']}")
            with col3:
                st.write(f"**Mood:** {entry['mood']}")
            with col4:
                st.write(f"**Rating:** {'*' * entry['rating']}")
            
            st.write(entry['content'])

def home_page():
    # Add custom CSS for the home page
    st.markdown("""
        <style>
        .home-content {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            text-align: center;
        }
        .home-content h3 {
            color: #264653;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
        }
        .instruction-section {
            background: rgba(42, 157, 143, 0.1);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            text-align: left;
        }
        .instruction-section strong {
            color: #2A9D8F;
        }
        .safety-notes {
            background: rgba(230, 57, 70, 0.1);
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 2rem;
        }
        .safety-notes h3 {
            color: #E63946;
        }
        .safety-notes ul {
            text-align: left;
            list-style-position: inside;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title using Streamlit's native title
    st.title("Scuba Diving Assistant Instructions")
    
    # Main content container
    st.markdown('<div class="home-content">', unsafe_allow_html=True)
    
    # How to Use section
    st.markdown('<h3>How to Use This Application</h3>', unsafe_allow_html=True)
    
    # 1. Logging a New Dive
    with st.container():
        st.markdown("""
            <div class="instruction-section">
                <strong>1. Logging a New Dive</strong>
                <ul>
                    <li>Click "Log New Dive" in the sidebar</li>
                    <li>Fill in dive details (date, location, depth, duration)</li>
                    <li>Add any buddy information and personal notes</li>
                    <li>Click "Save Dive Log" to store your entry</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # 2. Viewing Dive History
    with st.container():
        st.markdown("""
            <div class="instruction-section">
                <strong>2. Viewing Your Dive History</strong>
                <ul>
                    <li>Select "View Dive Logs" from the sidebar</li>
                    <li>Browse through your past dives</li>
                    <li>Use filters to find specific dives</li>
                    <li>Export logs if needed</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # 3. Planning Next Dive
    with st.container():
        st.markdown("""
            <div class="instruction-section">
                <strong>3. Planning Your Next Dive</strong>
                <ul>
                    <li>Go to "Dive Planner"</li>
                    <li>Enter your planned depth and time</li>
                    <li>The planner will calculate your pressure group</li>
                    <li>For repetitive dives, enter surface interval to get adjusted times</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # 4. Travel Planning
    with st.container():
        st.markdown("""
            <div class="instruction-section">
                <strong>4. Travel Planning</strong>
                <ul>
                    <li>Use "Travel Planner" for trip organization</li>
                    <li>Input destination and dates</li>
                    <li>Track equipment and documentation needs</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # 5. Weather Check
    with st.container():
        st.markdown("""
            <div class="instruction-section">
                <strong>5. Weather Check</strong>
                <ul>
                    <li>Check "Weather & Conditions" before your dive</li>
                    <li>View current conditions at dive sites</li>
                    <li>Make informed decisions about dive timing</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # 6. Keeping a Dive Journal
    with st.container():
        st.markdown("""
            <div class="instruction-section">
                <strong>6. Keeping a Dive Journal</strong>
                <ul>
                    <li>Select "Write Journal" to write about your experiences</li>
                    <li>Add detailed observations and memories</li>
                    <li>View past entries in "My Journals"</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Safety Notes
    with st.container():
        st.markdown("""
            <div class="safety-notes">
                <h3>Safety Notes</h3>
                <ul>
                    <li>Always follow safe diving practices</li>
                    <li>Stay within no-decompression limits</li>
                    <li>Plan your dives and dive your plan</li>
                    <li>Never dive alone</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Add tank logo to sidebar
    tank_image = get_tank_image_base64()
    st.sidebar.markdown(f"""
        <div style='text-align: center; padding: 2rem 0; margin: 1rem 0;'>
            <a href="/" style='text-decoration: none;'>
                <img src="{tank_image}" style='width: 150px; height: auto; margin-bottom: 1rem;' alt="Scuba Tank Logo">
                <div style='
                    font-family: "Marker Felt", "Comic Sans MS", cursive;
                    font-size: 32px;
                    color: #2A9D8F;
                    margin-top: 0.5rem;
                    line-height: 1.2;
                '>
                    Scuba<br>Assistant
                </div>
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    # Add global button hover style
    st.markdown("""
        <style>
        .stButton button {
            transition: color 0.3s;
        }
        .stButton button:hover {
            color: black !important;
        }
        
        /* Center print buttons */
        div[data-testid="stButton"] {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Set up navigation
    pages = {
        "Home": home_page,
        "Log New Dive": dive_log_page,
        "View Dive Logs": view_logs_page,
        "Dive Planner": dive_planner_page,
        "Travel Planner": travel_planner_page,
        "Weather & Conditions": weather_page,
        "Write Journal": journal_entry_page,
        "My Journals": view_journals_page
    }
    
    selection = st.sidebar.radio("", list(pages.keys()))
    pages[selection]()


if __name__ == "__main__":
    main()
