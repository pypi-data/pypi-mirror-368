"""
Unified descriptor utilities and patterns
"""
from typing import Any, Optional, Type, Union
from ..core import AccessLevel


def extract_function_from_descriptor(descriptor: Any) -> Optional[Any]:
    """
    Extract the underlying function from various descriptor types.
    Unified logic for consistent descriptor unwrapping across the codebase.
    """
    if isinstance(descriptor, (classmethod, staticmethod)):
        return descriptor.__func__
    elif hasattr(descriptor, '__func__'):
        return descriptor.__func__
    elif hasattr(descriptor, '_func_or_value'):
        return descriptor._func_or_value
    return None


def get_access_level_from_descriptor(descriptor: Any) -> Optional[AccessLevel]:
    """Extract access level from various descriptor types"""
    # Check direct access level
    if hasattr(descriptor, '_access_level'):
        return getattr(descriptor, '_access_level')
    
    # Check property.fget
    if isinstance(descriptor, property) and hasattr(descriptor.fget, '_access_level'):
        return getattr(descriptor.fget, '_access_level')
    
    # Check staticmethod.__func__
    if isinstance(descriptor, staticmethod) and hasattr(descriptor.__func__, '_access_level'):
        return getattr(descriptor.__func__, '_access_level')
    
    # Check classmethod.__func__
    if isinstance(descriptor, classmethod) and hasattr(descriptor.__func__, '_access_level'):
        return getattr(descriptor.__func__, '_access_level')
    
    return None


def get_friend_flag_from_descriptor(descriptor: Any) -> bool:
    """Extract friend decorator flag from various descriptor types"""
    # Check direct friend flag
    if hasattr(descriptor, '_created_by_friend_decorator'):
        return getattr(descriptor, '_created_by_friend_decorator', False)
    
    # Check property.fget
    if isinstance(descriptor, property) and hasattr(descriptor.fget, '_created_by_friend_decorator'):
        return getattr(descriptor.fget, '_created_by_friend_decorator', False)
    
    # Check staticmethod.__func__
    if isinstance(descriptor, staticmethod) and hasattr(descriptor.__func__, '_created_by_friend_decorator'):
        return getattr(descriptor.__func__, '_created_by_friend_decorator', False)
    
    # Check classmethod.__func__
    if isinstance(descriptor, classmethod) and hasattr(descriptor.__func__, '_created_by_friend_decorator'):
        return getattr(descriptor.__func__, '_created_by_friend_decorator', False)
    
    return False


def get_wrapper_info_from_descriptor(descriptor: Any) -> str:
    """Get descriptive wrapper information for error messages"""
    if isinstance(descriptor, property):
        return " (found in property.fget)"
    elif isinstance(descriptor, staticmethod):
        return " (found in staticmethod.__func__)"
    elif isinstance(descriptor, classmethod):
        return " (found in classmethod.__func__)"
    return ""


def is_descriptor_type(obj: Any, descriptor_types: Union[Type, tuple]) -> bool:
    """Check if object is one of the specified descriptor types"""
    if not isinstance(descriptor_types, tuple):
        descriptor_types = (descriptor_types,)
    return isinstance(obj, descriptor_types)


def get_safe_name(obj: Any, default: str = 'unknown') -> str:
    """Safely extract name from object, with fallback"""
    return getattr(obj, '__name__', default)


def get_safe_class_name(cls: Optional[Type], default: str = None) -> Optional[str]:
    """Safely extract class name with null safety"""
    return cls.__name__ if cls else default


def extract_qualname_parts(func: Any) -> list:
    """Extract and split qualname parts from function"""
    if hasattr(func, '__qualname__'):
        return func.__qualname__.split('.')
    return []


def is_private_name_mangled(name: str, class_name: str) -> bool:
    """Check if a name is Python private name-mangled"""
    return name.startswith(f'_{class_name}__')


def extract_original_private_name(mangled_name: str, class_name: str) -> str:
    """Extract original name from Python name-mangled private attribute"""
    if is_private_name_mangled(mangled_name, class_name):
        return '__' + mangled_name[len(f'_{class_name}__'):]
    return mangled_name
