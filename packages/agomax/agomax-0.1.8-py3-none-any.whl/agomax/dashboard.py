import subprocess
import os
import pkg_resources
import sys

def find_streamlit_app():
    """Find the streamlit_app.py file in the package installation."""
    
    # Method 1: Try pkg_resources (most reliable for installed packages)
    try:
        return pkg_resources.resource_filename('agomax', '../streamlit_app.py')
    except:
        pass
    
    # Method 2: Look relative to agomax package location
    try:
        import agomax
        agomax_dir = os.path.dirname(agomax.__file__)
        parent_dir = os.path.dirname(agomax_dir)
        streamlit_path = os.path.join(parent_dir, 'streamlit_app.py')
        if os.path.exists(streamlit_path):
            return streamlit_path
    except:
        pass
    
    # Method 3: Search in site-packages
    try:
        for path in sys.path:
            if 'site-packages' in path:
                streamlit_path = os.path.join(path, 'streamlit_app.py')
                if os.path.exists(streamlit_path):
                    return streamlit_path
    except:
        pass
    
    # Method 4: Development mode - look relative to current file
    try:
        current_dir = os.path.dirname(os.path.dirname(__file__))
        streamlit_path = os.path.join(current_dir, 'streamlit_app.py')
        if os.path.exists(streamlit_path):
            return streamlit_path
    except:
        pass
    
    return None

def dashboard():
    """Launch the Streamlit dashboard for Agomax."""
    try:
        # Find the streamlit app
        streamlit_path = find_streamlit_app()
        
        if not streamlit_path or not os.path.exists(streamlit_path):
            print("❌ Error: Could not find streamlit_app.py")
            print("🔍 Searched in multiple locations but streamlit_app.py was not found.")
            print("📦 Please ensure the package is properly installed:")
            print("   pip install agomax --upgrade")
            print("   or")
            print("   pip uninstall agomax && pip install agomax")
            return
            
        print(f"🚀 Launching Agomax dashboard from: {streamlit_path}")
        
        # Check if streamlit is installed
        try:
            import streamlit
        except ImportError:
            print("❌ Error: Streamlit is not installed")
            print("📦 Please install streamlit:")
            print("   pip install streamlit")
            return
            
        subprocess.run(['streamlit', 'run', streamlit_path])
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")
