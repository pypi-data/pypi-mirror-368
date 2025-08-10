import subprocess
import os
import pkg_resources

def dashboard():
    """Launch the Streamlit dashboard for Agomax."""
    try:
        # Try to find streamlit_app.py in the package directory
        package_dir = os.path.dirname(os.path.dirname(__file__))
        streamlit_path = os.path.join(package_dir, 'streamlit_app.py')
        
        if not os.path.exists(streamlit_path):
            # Try pkg_resources
            try:
                streamlit_path = pkg_resources.resource_filename('agomax', '../streamlit_app.py')
            except:
                # Fallback to current directory
                streamlit_path = 'streamlit_app.py'
        
        if not os.path.exists(streamlit_path):
            print("Error: Could not find streamlit_app.py")
            print("Make sure you are running from the Agomax package directory")
            return
            
        print(f"Launching Agomax dashboard at: {streamlit_path}")
        subprocess.run(['streamlit', 'run', streamlit_path])
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")
