"""
Naming convention utilities
"""
from ..core import AccessLevel


def detect_implicit_access_level(method_name: str) -> AccessLevel:
    """
    Detect access level from Python naming conventions:
    - __method = private (double underscore, but not dunder methods)
    - _method = protected (single underscore)
    - method = public (no underscore)
    """
    # Skip dunder methods (like __init__, __str__, etc.)
    if method_name.startswith('__') and method_name.endswith('__'):
        return AccessLevel.PUBLIC  # Dunder methods should remain public
    
    if method_name.startswith('__'):
        # Double underscore prefix (but not dunder methods)
        return AccessLevel.PRIVATE
    elif method_name.startswith('_'):
        # Single underscore prefix
        return AccessLevel.PROTECTED
    else:
        # No underscore prefix
        return AccessLevel.PUBLIC


def should_apply_implicit_access_control(method_name: str) -> bool:
    """Check if a method should have implicit access control applied"""
    # Don't apply to dunder methods
    if method_name.startswith('__') and method_name.endswith('__'):
        return False
    
    # Apply to methods with underscore prefixes
    return method_name.startswith('_')
