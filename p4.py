import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Battery Cell Monitor",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.37);
    }
    .cell-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        font-weight: bold;
    }
    .status-normal { background-color: #28a745; color: white; }
    .status-warning { background-color: #ffc107; color: black; }
    .status-critical { background-color: #dc3545; color: white; }
    .stSelectbox > div > div > select {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'cell_types' not in st.session_state:
    st.session_state.cell_types = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

def get_cell_specs(cell_type):
    """Get specifications for different cell types"""
    specs = {
        "lfp": {
            "voltage": 3.2,
            "min_voltage": 2.8,
            "max_voltage": 3.6,
            "color": "#2E8B57"
        },
        "nmc": {
            "voltage": 3.6,
            "min_voltage": 3.2,
            "max_voltage": 4.0,
            "color": "#4169E1"
        },
        "lco": {
            "voltage": 3.7,
            "min_voltage": 3.0,
            "max_voltage": 4.2,
            "color": "#FF6347"
        },
        "lmo": {
            "voltage": 3.8,
            "min_voltage": 3.2,
            "max_voltage": 4.3,
            "color": "#32CD32"
        }
    }
    return specs.get(cell_type.lower(), specs["nmc"])

def generate_cell_data(cell_type, cell_id):
    """Generate realistic cell data with some variation"""
    specs = get_cell_specs(cell_type)
    
    # Add some realistic variation to voltage
    voltage_variation = random.uniform(-0.1, 0.1)
    voltage = max(specs["min_voltage"], 
                 min(specs["max_voltage"], 
                     specs["voltage"] + voltage_variation))
    
    current = round(random.uniform(-5.0, 5.0), 2)  # Can be charging (negative) or discharging (positive)
    temp = round(random.uniform(25, 45), 1)
    capacity = round(abs(voltage * current), 2)  # Capacity as power
    
    return {
        "voltage": round(voltage, 2),
        "current": current,
        "temp": temp,
        "capacity": capacity,
        "min_voltage": specs["min_voltage"],
        "max_voltage": specs["max_voltage"],
        "color": specs["color"]
    }

def get_cell_status(cell_data):
    """Determine cell status based on voltage and temperature"""
    voltage = cell_data["voltage"]
    temp = cell_data["temp"]
    min_v = cell_data["min_voltage"]
    max_v = cell_data["max_voltage"]
    
    if voltage < min_v * 1.05 or voltage > max_v * 0.95 or temp > 40:
        return "critical", "⚠️"
    elif voltage < min_v * 1.1 or voltage > max_v * 0.9 or temp > 35:
        return "warning", "⚡"
    else:
        return "normal", "✅"

# Main UI
st.markdown('<h1 class="main-header">🔋 Battery Cell Monitoring System</h1>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Cell type selection
    st.subheader("Cell Types Setup")
    num_cells = st.slider("Number of Cells", 1, 12, 8)
    
    cell_types = []
    for i in range(num_cells):
        cell_type = st.selectbox(
            f"Cell #{i+1} Type",
            ["LFP", "NMC", "LCO", "LMO"],
            key=f"cell_type_{i}"
        )
        cell_types.append(cell_type.lower())
    
    st.session_state.cell_types = cell_types
    
    st.divider()
    
    # Refresh controls
    st.subheader("🔄 Data Refresh")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Update Data", type="primary"):
            # Generate new data for all cells
            st.session_state.cells_data = {}
            for idx, cell_type in enumerate(st.session_state.cell_types, start=1):
                cell_key = f"cell_{idx}_{cell_type}"
                st.session_state.cells_data[cell_key] = generate_cell_data(cell_type, idx)
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("Auto Refresh", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh
    
    if auto_refresh:
        refresh_rate = st.slider("Refresh Rate (seconds)", 1, 10, 3)
        time.sleep(refresh_rate)
        st.rerun()

# Generate initial data if not exists
if not st.session_state.cells_data and st.session_state.cell_types:
    for idx, cell_type in enumerate(st.session_state.cell_types, start=1):
        cell_key = f"cell_{idx}_{cell_type}"
        st.session_state.cells_data[cell_key] = generate_cell_data(cell_type, idx)

# Main dashboard
if st.session_state.cells_data:
    # Overview metrics
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_voltage = sum(data["voltage"] for data in st.session_state.cells_data.values())
    avg_temp = sum(data["temp"] for data in st.session_state.cells_data.values()) / len(st.session_state.cells_data)
    total_current = sum(data["current"] for data in st.session_state.cells_data.values())
    total_capacity = sum(data["capacity"] for data in st.session_state.cells_data.values())
    
    with col1:
        st.metric("Total Voltage", f"{total_voltage:.2f} V", delta=f"{random.uniform(-0.1, 0.1):.2f}")
    with col2:
        st.metric("Average Temperature", f"{avg_temp:.1f} °C", delta=f"{random.uniform(-1, 1):.1f}")
    with col3:
        st.metric("Total Current", f"{total_current:.2f} A", delta=f"{random.uniform(-0.5, 0.5):.2f}")
    with col4:
        st.metric("Total Capacity", f"{total_capacity:.2f} W", delta=f"{random.uniform(-2, 2):.2f}")
    
    st.divider()
    
    # Cell status grid
    st.header("🔋 Individual Cell Status")
    
    # Create a grid of cell statuses
    cols_per_row = 4
    rows = (len(st.session_state.cells_data) + cols_per_row - 1) // cols_per_row
    
    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            cell_idx = row * cols_per_row + col_idx
            if cell_idx < len(st.session_state.cells_data):
                cell_key = list(st.session_state.cells_data.keys())[cell_idx]
                cell_data = st.session_state.cells_data[cell_key]
                status, icon = get_cell_status(cell_data)
                
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="cell-status status-{status}">
                        {icon} {cell_key.replace('_', ' ').title()}<br>
                        {cell_data['voltage']:.2f}V | {cell_data['temp']:.1f}°C
                    </div>
                    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Detailed visualizations
    st.header("📈 Detailed Analytics")
    
    # Create DataFrame for easier plotting
    df_data = []
    for cell_key, cell_data in st.session_state.cells_data.items():
        df_data.append({
            'Cell': cell_key.replace('_', ' ').title(),
            'Type': cell_key.split('_')[2].upper(),
            'Voltage': cell_data['voltage'],
            'Current': cell_data['current'],
            'Temperature': cell_data['temp'],
            'Capacity': cell_data['capacity'],
            'Status': get_cell_status(cell_data)[0]
        })
    
    df = pd.DataFrame(df_data)
    
    # Voltage and Temperature Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_voltage = px.bar(
            df, x='Cell', y='Voltage', color='Type',
            title='Cell Voltages',
            color_discrete_map={'LFP': '#2E8B57', 'NMC': '#4169E1', 'LCO': '#FF6347', 'LMO': '#32CD32'}
        )
        fig_voltage.update_layout(showlegend=True, height=400)
        st.plotly_chart(fig_voltage, use_container_width=True)
    
    with col2:
        fig_temp = px.scatter(
            df, x='Cell', y='Temperature', color='Type', size='Capacity',
            title='Temperature vs Capacity',
            color_discrete_map={'LFP': '#2E8B57', 'NMC': '#4169E1', 'LCO': '#FF6347', 'LMO': '#32CD32'}
        )
        fig_temp.update_layout(showlegend=True, height=400)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Current flow visualization
    fig_current = px.bar(
        df, x='Cell', y='Current', color='Current',
        title='Current Flow (Positive: Discharge, Negative: Charge)',
        color_continuous_scale='RdBu_r'
    )
    fig_current.update_layout(height=400)
    st.plotly_chart(fig_current, use_container_width=True)
    
    # Data table
    st.header("📋 Detailed Data Table")
    st.dataframe(df, use_container_width=True)
    
    # Export functionality
    st.header("💾 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"battery_data_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"battery_data_{time.strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

else:
    st.info("👆 Please configure your cell types in the sidebar and click 'Update Data' to begin monitoring!")
    
    # Show sample configuration
    st.subheader("🔧 Quick Start Guide")
    st.write("""
    1. **Configure Cells**: Use the sidebar to set the number of cells and their types
    2. **Update Data**: Click the 'Update Data' button to generate initial readings
    3. **Monitor**: Watch real-time data with auto-refresh enabled
    4. **Analyze**: Use the charts and tables to analyze performance
    5. **Export**: Download your data in CSV or JSON format
    """)
    
    st.subheader("🔋 Supported Cell Types")
    cell_info = pd.DataFrame({
        'Type': ['LFP', 'NMC', 'LCO', 'LMO'],
        'Full Name': ['Lithium Iron Phosphate', 'Lithium Nickel Manganese Cobalt', 'Lithium Cobalt Oxide', 'Lithium Manganese Oxide'],
        'Nominal Voltage': ['3.2V', '3.6V', '3.7V', '3.8V'],
        'Voltage Range': ['2.8V - 3.6V', '3.2V - 4.0V', '3.0V - 4.2V', '3.2V - 4.3V']
    })
    st.dataframe(cell_info, use_container_width=True)