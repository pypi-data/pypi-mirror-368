"""
Descriptor for properties with access control
"""
from .base import AccessControlledDescriptor


class PropertyDescriptor(AccessControlledDescriptor):
    """Descriptor for properties"""
    
    def __init__(self, fget, access_level, fset=None, fdel=None, doc=None):
        super().__init__(fget, access_level)
        self._fset = fset
        self._fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self._func_or_value is None:
            raise AttributeError("unreadable attribute")
        
        self._check_access(obj)
        return self._func_or_value(obj)
    
    def __set__(self, obj, value):
        if self._fset is None:
            raise AttributeError("can't set attribute")
        self._check_access(obj)
        self._fset(obj, value)
    
    def __delete__(self, obj):
        if self._fdel is None:
            raise AttributeError("can't delete attribute")
        self._check_access(obj)
        self._fdel(obj)
    
    def setter(self, func):
        """Return a new property with the setter function"""
        return PropertyDescriptor(self._func_or_value, self._access_level, func, self._fdel, self.__doc__)
    
    def deleter(self, func):
        """Return a new property with the deleter function"""
        return PropertyDescriptor(self._func_or_value, self._access_level, self._fset, func, self.__doc__)
    
    def _get_member_type(self) -> str:
        return "property"
