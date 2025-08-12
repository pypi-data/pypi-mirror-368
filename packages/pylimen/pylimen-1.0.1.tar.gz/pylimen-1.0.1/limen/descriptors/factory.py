"""
Factory for creating appropriate descriptors
"""
from typing import Callable
from ..core import AccessLevel
from .base import AccessControlledDescriptor
from .method import MethodDescriptor
from .static_method import StaticMethodDescriptor
from .class_method import ClassMethodDescriptor
from .property import PropertyDescriptor


class DescriptorFactory:
    """Factory for creating appropriate descriptors"""
    
    @staticmethod
    def create_method_descriptor(func: Callable, access_level: AccessLevel) -> AccessControlledDescriptor:
        """Create appropriate method descriptor based on function type"""
        # Check for friend method decoration before creating descriptor
        DescriptorFactory._register_friend_method_if_needed(func)
        
        # Handle different function types with unified logic
        descriptor_map = {
            staticmethod: (StaticMethodDescriptor, lambda f: f.__func__),
            classmethod: (ClassMethodDescriptor, lambda f: f.__func__),
            property: (PropertyDescriptor, lambda f: DescriptorFactory._create_property_descriptor(f, access_level))
        }
        
        for func_type, (descriptor_class, extractor) in descriptor_map.items():
            if isinstance(func, func_type):
                if func_type is property:
                    return extractor(func)  # Special handling for property
                else:
                    underlying_func = extractor(func)
                    DescriptorFactory._register_friend_method_if_needed(underlying_func)
                    return descriptor_class(underlying_func, access_level)
        
        # Default case: regular method
        return MethodDescriptor(func, access_level)
    
    @staticmethod
    def _create_property_descriptor(prop: property, access_level: AccessLevel) -> PropertyDescriptor:
        """Create property descriptor with friend registration"""
        DescriptorFactory._register_friend_method_if_needed(prop.fget)
        return PropertyDescriptor(prop.fget, access_level, prop.fset, prop.fdel, prop.__doc__)
    
    @staticmethod
    def _register_friend_method_if_needed(func: Callable) -> None:
        """Register a method as a friend if it was decorated with @friend"""
        if func and hasattr(func, '_limen_friend_target') and hasattr(func, '_limen_is_friend_method'):
            # We can't register now because we don't know the owner class yet
            # The descriptor will handle this in __set_name__
            pass
