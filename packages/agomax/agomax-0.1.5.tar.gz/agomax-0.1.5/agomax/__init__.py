#"""
Agomax v0.1.5 - Universal Drone Anomaly Detection Python Package
"""

__version__ = "0.1.5"ax package init
"""
Agomax - Universal Drone Anomaly Detection Python Package
"""

__version__ = "0.1.4"

# Import main functions
try:
    from .dashboard import dashboard
    from .detect import agomax_detect
    __all__ = ["dashboard", "agomax_detect"]
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    __all__ = []
