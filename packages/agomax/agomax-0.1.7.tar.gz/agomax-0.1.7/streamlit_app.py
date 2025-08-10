import streamlit as st
import pandas as pd
import plotly.express as px
import os
import pkg_resources
from agomax.detect import agomax_detect

st.set_page_config(page_title="Agomax Drone Anomaly Detection", layout="wide")
st.title("Agomax Drone Anomaly Detection Dashboard")

# --- Introduction Window ---
st.sidebar.title("Welcome to Agomax Drone Anomaly Detection Dashboard")
st.sidebar.markdown("""
**Instructions:**
- This dashboard detects anomalies in drone telemetry using machine learning and rule-based logic.
- You can test the system in two modes:
    1. **Offline CSV:** Upload a telemetry file or use the provided demo file to see how anomaly detection works.
    2. **Live Stream:** Connect to a live drone telemetry stream for real-time detection.
- For first-time users, start with the Offline CSV mode and explore the results using the demo data.
""")

mode = st.sidebar.selectbox("Select Mode", ["Offline CSV", "Live Stream"])

# Dynamic path resolution for configs and models
def get_resource_path(relative_path):
    """Get the absolute path to a resource file."""
    try:
        # Try pkg_resources first (when installed as package)
        return pkg_resources.resource_filename('agomax', f'../{relative_path}')
    except:
        # Fallback to relative path (when running from source)
        return relative_path

rules_path = get_resource_path('configs/rules.yaml')
model_dir = get_resource_path('models/')

if mode == "Offline CSV":
    st.header("Offline CSV Demo: Test Anomaly Detection")
    st.markdown("""
**How to use:**
- By default, the dashboard loads a demo file (`crash.csv`) from the `data/` folder to show how anomaly detection works.
- You can also upload your own telemetry CSV file using the sidebar.
""")
    uploaded_file = st.sidebar.file_uploader("Upload Telemetry CSV", type=["csv"], key="csv_uploader_demo")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        demo_label = "Detection complete! (Your file)"
    else:
        try:
            # Try to load demo file from package
            demo_path = get_resource_path('data/crash.csv')
            df = pd.read_csv(demo_path)
            demo_label = "Detection complete! (Demo: crash.csv)"
        except Exception as e:
            st.error(f"Could not load demo file: {e}")
            st.error("Please upload your own CSV file to continue.")
            df = None
    
    if df is not None:
        result = agomax_detect(df, mode='live', rules_path=rules_path, model_dir=model_dir)
        st.success(demo_label)
        st.dataframe(result.head(20))

        # Live Status Indicator
        anomaly_count = result['anomaly_flag'].sum()
        total = len(result)
        status = "Anomaly" if anomaly_count > 0 else "Normal"
        color = "red" if anomaly_count > 0 else "green"
        st.markdown(f"## <span style='color:{color};font-size:48px'>{status}</span>", unsafe_allow_html=True)

        # Time-series plot
        if 'timestamp' in result.columns:
            fig = px.line(result, x='timestamp', y='anomaly_flag', title='Anomaly Timeline')
            fig.add_scatter(x=result['timestamp'][result['anomaly_flag']], y=[1]*anomaly_count, mode='markers', marker=dict(color='red', size=10), name='Anomaly')
            st.plotly_chart(fig, use_container_width=True)

        # Rule Violations Table
        st.subheader("Rule Violations Table")
        st.dataframe(result[['timestamp', 'broken_rules_count', 'violated_rules_list']])

        # Ensemble Votes Table
        st.subheader("Ensemble Votes Table")
        st.dataframe(result[['timestamp', 'kmeans_pred', 'lof_pred', 'svm_pred', 'dbscan_pred', 'optics_pred', 'final_vote']])

        # Summary Stats
        st.subheader("Summary Stats")
        st.write(f"Total anomalies: {anomaly_count}")
        st.write(f"Percentage: {anomaly_count/total*100:.2f}%")
        st.write(f"Detection rate: {anomaly_count/total:.2f}")

else:
    import time
    try:
        from dronekit import connect
    except ImportError:
        st.error("DroneKit not installed. Run 'pip install dronekit' in your environment.")
        st.stop()

    st.subheader("Live Drone Telemetry Stream (MAVLink/DroneKit)")
    connection_str = st.text_input("Enter MAVLink connection string", "udp:127.0.0.1:14550")
    buffer_size = st.number_input("Rolling buffer size", min_value=10, max_value=500, value=100)
    start_stream = st.button("Start Live Detection")

    if start_stream:
        status_placeholder = st.empty()
        table_placeholder = st.empty()
        plot_placeholder = st.empty()
        try:
            vehicle = connect(connection_str, wait_ready=True)
        except Exception as e:
            st.error(f"Could not connect to vehicle: {e}")
            st.stop()

        telemetry_buffer = []
        while True:
            # Get latest telemetry
            try:
                row = {
                    'timestamp': time.time(),
                    'roll': getattr(vehicle.attitude, 'roll', 0),
                    'pitch': getattr(vehicle.attitude, 'pitch', 0),
                    'yaw': getattr(vehicle.attitude, 'yaw', 0),
                    'rollspeed': getattr(vehicle.gyro, 'x', 0) if hasattr(vehicle, 'gyro') else 0,
                    'pitchspeed': getattr(vehicle.gyro, 'y', 0) if hasattr(vehicle, 'gyro') else 0,
                    'yawspeed': getattr(vehicle.gyro, 'z', 0) if hasattr(vehicle, 'gyro') else 0,
                    'airspeed': getattr(vehicle, 'airspeed', 0),
                    'GPS_status': 1,
                    'Gyro_status': 1,
                    'Accel_status': 1,
                }
            except Exception as e:
                st.error(f"Telemetry error: {e}")
                break
            telemetry_buffer.append(row)
            if len(telemetry_buffer) > buffer_size:
                telemetry_buffer.pop(0)
            df = pd.DataFrame(telemetry_buffer)
            if len(df) >= 50:
                result = agomax_detect(df, mode='live', rules_path=rules_path, model_dir=model_dir)
                anomaly_count = result['anomaly_flag'].sum()
                total = len(result)
                status = "Anomaly" if anomaly_count > 0 else "Normal"
                color = "red" if anomaly_count > 0 else "green"
                status_placeholder.markdown(f"## <span style='color:{color};font-size:48px'>{status}</span>", unsafe_allow_html=True)
                table_placeholder.dataframe(result.tail(20))
                if 'timestamp' in result.columns:
                    import plotly.express as px
                    fig = px.line(result, x='timestamp', y='anomaly_flag', title='Live Anomaly Timeline')
                    fig.add_scatter(x=result['timestamp'][result['anomaly_flag']], y=[1]*anomaly_count, mode='markers', marker=dict(color='red', size=10), name='Anomaly')
                    plot_placeholder.plotly_chart(fig, use_container_width=True)
            else:
                status_placeholder.warning("Waiting for at least 50 telemetry samples for full anomaly detection...")
                table_placeholder.dataframe(df.tail(20))
            time.sleep(1)
