"""
Abstract base class for access-controlled descriptors
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Type
from ..core import AccessLevel


class MethodWrapperMixin:
    """Mixin providing common wrapper functionality for method descriptors"""
    
    def _create_wrapper_with_context(self, wrapper_func, context_data=None):
        """Create a wrapper function with limen context attributes"""
        # Store the owner class and method name for stack inspection
        wrapper_func._limen_owner_class = self._owner  
        wrapper_func._limen_method_name = self._name
        
        # Store any additional context data
        if context_data:
            for key, value in context_data.items():
                setattr(wrapper_func, key, value)
        
        return wrapper_func


class AccessControlledDescriptor(ABC, MethodWrapperMixin):
    """Abstract base class for access-controlled descriptors"""
    
    def __init__(self, func_or_value: Any, access_level: AccessLevel):
        self._func_or_value = func_or_value
        self._access_level = access_level
        self._name: Optional[str] = None
        self._owner: Optional[Type] = None
        
        # Preserve function attributes
        if hasattr(func_or_value, '__name__'):
            self.__name__ = func_or_value.__name__
    
    def __set_name__(self, owner: Type, name: str) -> None:
        """Called when descriptor is assigned to a class attribute"""
        self._name = name
        self._owner = owner
        # Import here to avoid circular import
        from ..system.access_control import get_access_control_system
        access_control = get_access_control_system()
        access_control.register_method(owner.__name__, name, self._access_level)
        
        # Check if this method was decorated with @friend and register it
        self._register_friend_method_if_needed(access_control, owner, name)
    
    def _register_friend_method_if_needed(self, access_control, owner: Type, name: str) -> None:
        """Register method as friend if it was decorated with @friend"""
        func = self._func_or_value
        
        # Check the function itself
        if hasattr(func, '_limen_friend_target') and hasattr(func, '_limen_is_friend_method'):
            target_class = func._limen_friend_target
            access_control.register_friend_method(target_class, owner, name)
            access_control.emit_event('friend_method_established', {
                'target_class': target_class.__name__,
                'friend_class': owner.__name__,
                'method_name': name
            })
            # Clean up the temporary attributes
            delattr(func, '_limen_friend_target')
            delattr(func, '_limen_is_friend_method')
    
    @abstractmethod
    def __get__(self, obj, objtype=None):
        """Abstract method for descriptor access"""
        pass
    
    def _check_access(self, obj=None) -> None:
        """Check access permissions"""
        # Import here to avoid circular import
        from ..system.access_control import get_access_control_system
        from ..inspection.stack_inspector import StackInspector

        access_control = get_access_control_system()

        # If enforcement is disabled, allow all access
        if not access_control.enforcement_enabled:
            return
        
        # Safety check: if _owner is None, __set_name__ hasn't been called yet
        # This can happen during class construction - allow access in this case
        if self._owner is None or self._name is None:
            return

        # Get caller info from stack
        stack_inspector = StackInspector()
        caller_info = stack_inspector.get_caller_info()

        # Note: We don't apply fallback logic here anymore
        # If stack inspection fails, caller_info.caller_class will be None
        # which correctly represents external/module-level access
        
        # Use the access checker directly with our caller info
        if hasattr(access_control, '_access_checker'):
            # Pass instance class for inheritance analysis
            instance_class = obj.__class__ if obj is not None else None
            result = access_control._access_checker.can_access(
                self._owner, self._name, self._access_level, caller_info, instance_class
            )
        else:
            result = access_control.check_access(self._owner, self._name, self._access_level)
        
        if not result:
            from ..exceptions import PermissionDeniedError
            raise PermissionDeniedError(
                self._access_level.value, 
                self._get_member_type(), 
                self._name
            )
    
    @abstractmethod
    def _get_member_type(self) -> str:
        """Get the type of member (method, property, etc.)"""
        pass
