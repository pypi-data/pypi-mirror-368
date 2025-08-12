"""
Descriptor for class methods
"""
from functools import wraps
from .base import AccessControlledDescriptor


class ClassMethodDescriptor(AccessControlledDescriptor):
    """Descriptor for class methods"""
    
    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj)
        
        @wraps(self._func_or_value)
        def wrapper(*args, **kwargs):
            # For classmethods, obj could be None when called on the class
            # We use objtype as the effective class for access checking
            check_obj = obj if obj is not None else objtype
            self._check_access(check_obj)
            return self._func_or_value(objtype, *args, **kwargs)
        
        return self._create_wrapper_with_context(wrapper)
    
    def _get_member_type(self) -> str:
        return "class method"
