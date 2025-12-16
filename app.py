import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import pandas as pd
from PIL import Image
import time

# --- 1. PAGE CONFIGURATION & DARK THEME CSS ---
st.set_page_config(
    page_title="LabLens Access",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Dark Theme
st.markdown("""
<style>
    /* Hide Streamlit default menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Login Box Styling - Dark Mode */
    .stTextInput > div > div > input {
        text-align: center; 
        font-size: 1.2rem; 
        border: 2px solid #4A90E2;
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Dashboard Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Metric Colors */
    div[data-testid="stMetricLabel"] > label {color: #AAAAAA !important;}
    div[data-testid="stMetricValue"] {color: #FFFFFF !important;}
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE MANAGEMENT ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'inventory_df' not in st.session_state:
    st.session_state.inventory_df = pd.DataFrame(
        columns=["Timestamp", "Component Name", "Category", "Count", "Confidence"]
    )

# --- 3. THE TOOL LOGIC (Backend) ---
def update_inventory_tool(component_name: str, count: int, category: str):
    timestamp = time.strftime("%H:%M:%S")
    new_entry = pd.DataFrame([{
        "Timestamp": timestamp,
        "Component Name": component_name,
        "Category": category,
        "Count": count,
        "Confidence": "High 🟢"
    }])
    st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, new_entry], ignore_index=True)
    return {"status": "success", "added": f"{count} x {component_name}"}

# --- 4. VIEW 1: THE LOGIN SCREEN ---
if not st.session_state.authenticated:
    # Use 3 columns to center the middle block
    col1, col2, col3 = st.columns([1, 0.8, 1]) # 0.8 makes the login box slightly narrower/cleaner
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # CENTERED IMAGE using Flexbox (The most robust way)
        st.markdown(
            """
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <img src="https://cdn-icons-png.flaticon.com/512/900/900967.png" width="100">
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Title
        st.markdown("<h1 style='text-align: center; color: #4A90E2;'>LabLens Secure Access</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #BBB;'>Please enter your <b>Gemini API Key</b> to initialize the inventory system.</p>", unsafe_allow_html=True)
        
        # Input
        entered_key = st.text_input("API Key", type="password", placeholder="Paste your Google AI Studio Key here...", label_visibility="collapsed")
        
        # --- FIX: FULL WIDTH BUTTON ---
        # use_container_width=True forces the button to fill the column width, making it perfectly centered
        if st.button("🚀 Connect to System", type="primary", use_container_width=True):
            if entered_key.startswith("AIza"):
                st.session_state.api_key = entered_key
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid API Key format. It usually starts with 'AIza'.")
                
    st.stop()

# --- 5. VIEW 2: THE MAIN DASHBOARD ---

# Sidebar
with st.sidebar:
    st.success("✅ System Connected")
    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.session_state.api_key = ""
        st.rerun()
    st.markdown("---")
    st.markdown("**Model:** `Gemini 2.5-Flash`")
    st.markdown("**Status:** `Online`")

# TOP SECTION: METRICS
st.markdown("<h1 style='color: #4A90E2;'>🔬 LabLens Dashboard</h1>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
total_items = st.session_state.inventory_df["Count"].sum()
unique_types = st.session_state.inventory_df["Component Name"].nunique()
last_scan = st.session_state.inventory_df["Timestamp"].iloc[-1] if not st.session_state.inventory_df.empty else "--:--"

m1.metric("📦 Total Components", total_items)
m2.metric("🧩 Unique Types", unique_types)
m3.metric("🕒 Last Scan", last_scan)
m4.metric("⚡ System Latency", "120ms", delta="Optimal")

st.markdown("---")

# MAIN CONTENT
left_col, right_col = st.columns([1, 1.5], gap="large")

with left_col:
    st.subheader("📸 Scan Workspace")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Live Feed", use_container_width=True)
        
        if st.button("🔍 Analyze Components", type="primary", use_container_width=True):
            with st.status("Processing...", expanded=True) as status:
                try:
                    genai.configure(api_key=st.session_state.api_key)
                    
                    tools_config = {'function_declarations': [{
                        'name': 'update_inventory_tool',
                        'description': 'Updates database with detected components.',
                        'parameters': {
                            'type_': "OBJECT",
                            'properties': {
                                'component_name': {'type_': "STRING"},
                                'count': {'type_': "INTEGER"},
                                'category': {'type_': "STRING"}
                            },
                            'required': ['component_name', 'count', 'category']
                        }
                    }]}
                    
                    model = genai.GenerativeModel('gemini-2.5-flash', tools=[tools_config])
                    
                    retry_count = 0
                    while retry_count < 3:
                        try:
                            response = model.generate_content(
                                ["Analyze this image. Call 'update_inventory_tool' for every component seen.", image]
                            )
                            break
                        except exceptions.ResourceExhausted:
                            st.warning(f"Rate limit. Retrying... ({retry_count+1}/3)")
                            time.sleep(5)
                            retry_count += 1
                    
                    if response and response.parts:
                        call_found = False
                        for part in response.parts:
                            if fn := part.function_call:
                                call_found = True
                                update_inventory_tool(fn.args["component_name"], int(fn.args["count"]), fn.args["category"])
                        
                        if call_found:
                            status.update(label="Complete!", state="complete", expanded=False)
                            st.rerun()
                        else:
                            st.error("No components identified.")
                            
                except Exception as e:
                    st.error(f"Error: {e}")

with right_col:
    st.subheader("📊 Live Inventory Data")
    
    st.data_editor(
        st.session_state.inventory_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        height=400,
        column_config={
            "Timestamp": st.column_config.TextColumn("Time", width="small"),
            "Confidence": st.column_config.TextColumn("Status", width="small"),
            "Count": st.column_config.NumberColumn("Qty", format="%d"),
        }
    )
    
    if st.button("🗑️ Reset Database", type="secondary", use_container_width=True):
        st.session_state.inventory_df = pd.DataFrame(columns=["Timestamp", "Component Name", "Category", "Count", "Confidence"])
        st.rerun()