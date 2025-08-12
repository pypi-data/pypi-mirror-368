"""
Limen Access Control System - Refactored with better design patterns

A comprehensive access control system for Python classes that provides:
- C++ style access levels (private, protected, public) 
- Friend relationships
- Inheritance access control
- Property setter access control
- Decorator conflict detection

Example usage:
    from limen import private, protected, public, friend

    class MyClass:
        @private
        def _internal_method(self):
            return "secret"
        
        @protected
        @property
        def data(self):
            return self._data
        
        @data.setter
        def data(self, value):
            self._data = value
    
    @friend(MyClass)
    class FriendClass:
        def access_friend_data(self, obj):
            return obj._internal_method()
"""

# Initialize the system early
from .system import get_access_control_system
_access_control = get_access_control_system()

# Public API exports
from .decorators import private, protected, public, friend
from .system import enable_enforcement, disable_enforcement, get_metrics, reset_system
from .core import AccessLevel, InheritanceType
from .exceptions import (
    LimenError,
    PermissionDeniedError, 
    DecoratorConflictError,
    DecoratorUsageError
)

__all__ = [
    # Core decorators
    'private', 'protected', 'public', 'friend',
    
    # Management functions
    'enable_enforcement', 'disable_enforcement', 'reset_system', 'get_metrics',
    
    # Core types
    'AccessLevel', 'InheritanceType',
    
    # Exceptions
    'LimenError', 'PermissionDeniedError', 'DecoratorConflictError',
    'DecoratorUsageError'
]

__version__ = "1.0.2"
__author__ = "Limen Development Team"
__description__ = "C++ style access control for Python classes"
