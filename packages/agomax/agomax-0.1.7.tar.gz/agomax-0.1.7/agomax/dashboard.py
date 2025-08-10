import subprocess
import os
import pkg_resources

def get_resource_path(filename):
    """Get the path to a resource file included with the package."""
    try:
        # Try pkg_resources first
        return pkg_resources.resource_filename('agomax', f'../{filename}')
    except:
        try:
            # Try relative to package directory
            package_dir = os.path.dirname(os.path.dirname(__file__))
            path = os.path.join(package_dir, filename)
            if os.path.exists(path):
                return path
        except:
            pass
    
    # Fallback to filename as-is
    return filename

def dashboard():
    """Launch the Streamlit dashboard for Agomax."""
    try:
        # Get the streamlit app path
        streamlit_path = get_resource_path('streamlit_app.py')
        
        if not os.path.exists(streamlit_path):
            print("Error: Could not find streamlit_app.py")
            print("Make sure you are running from the Agomax package directory or the package is properly installed")
            return
            
        print(f"Launching Agomax dashboard at: {streamlit_path}")
        subprocess.run(['streamlit', 'run', streamlit_path])
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")
