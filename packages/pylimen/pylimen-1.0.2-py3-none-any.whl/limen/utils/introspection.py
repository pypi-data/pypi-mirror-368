"""
Method introspection utilities
"""
from typing import Type, Optional


def get_method_owner_class(func, instance_class: Type) -> Type:
    """Find the class that actually defines the given method"""
    method_name = func.__name__
    
    for cls in instance_class.__mro__:
        if hasattr(cls, method_name) and method_name in cls.__dict__:
            return cls
    
    return instance_class


def find_method_defining_class(instance, method_name: str) -> Type:
    """Find the class that actually defines the given method"""
    instance_class = type(instance)
    
    for cls in instance_class.__mro__:
        if hasattr(cls, method_name) and method_name in cls.__dict__:
            return cls
    
    return instance_class


def get_original_method_access_level(cls: Type, method_name: str):
    """Get the original access level of a method based on decorators or naming"""
    from ..core import AccessLevel
    
    if hasattr(cls, method_name):
        method = getattr(cls, method_name)
        
        # Check if method has explicit access level
        if hasattr(method, '_access_level'):
            return AccessLevel(method._access_level)
        
        # Check based on naming conventions
        if method_name.startswith('__') and not method_name.endswith('__'):
            return AccessLevel.PRIVATE
        elif method_name.startswith('_'):
            return AccessLevel.PROTECTED
        else:
            return AccessLevel.PUBLIC
    
    return AccessLevel.PUBLIC
