"""
System management functions
"""
import gc
from .access_control import get_access_control_system


def enable_enforcement() -> str:
    """Enable access control enforcement"""
    access_control = get_access_control_system()
    access_control.enforcement_enabled = True
    return "Access control enforcement enabled"


def disable_enforcement() -> str:
    """Disable access control enforcement"""
    access_control = get_access_control_system()
    access_control.enforcement_enabled = False
    return "Access control enforcement disabled"


def get_metrics() -> dict:
    """Get system metrics"""
    access_control = get_access_control_system()
    return access_control.get_metrics()


def reset_system() -> str:
    """Reset the access control system"""
    access_control = get_access_control_system()
    access_control.reset()
    
    # Clean up wrapped methods
    for obj in gc.get_objects():
        if hasattr(obj, '_limen_wrapped'):
            try:
                delattr(obj, '_limen_wrapped')
            except (AttributeError, TypeError):
                pass
    
    return "Access control system reset"
