"""
Descriptor for static methods
"""
import threading
from functools import wraps
from .base import AccessControlledDescriptor

# Thread-local storage for staticmethod caller context
_thread_local = threading.local()


class StaticMethodDescriptor(AccessControlledDescriptor):
    """Descriptor for static methods"""
    
    def __get__(self, obj, objtype=None):
        @wraps(self._func_or_value)
        def wrapper(*args, **kwargs):
            # Handle thread-local context for friend staticmethods
            context_manager = self._get_friend_context_manager()
            
            try:
                with context_manager:
                    self._check_access(obj)
                    return self._func_or_value(*args, **kwargs)
            finally:
                pass  # Context manager handles cleanup
        
        return self._create_wrapper_with_context(wrapper)
    
    def _get_friend_context_manager(self):
        """Get a context manager for friend staticmethod context"""
        return FriendStaticMethodContext(self._owner, self._name, self._is_friend_method())
    
    def _is_friend_method(self):
        """Check if this staticmethod is a friend method"""
        return (hasattr(self._func_or_value, '_friend_classes') and 
                self._func_or_value._friend_classes)

    def _get_member_type(self) -> str:
        return "static method"


class FriendStaticMethodContext:
    """Context manager for friend staticmethod thread-local storage"""
    
    def __init__(self, owner_class, method_name, is_friend):
        self.owner_class = owner_class
        self.method_name = method_name
        self.is_friend = is_friend
        self.old_context = None
    
    def __enter__(self):
        if self.is_friend:
            self.old_context = getattr(_thread_local, 'staticmethod_context', None)
            _thread_local.staticmethod_context = {
                'caller_class': self.owner_class,
                'caller_method': self.method_name
            }
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_friend:
            _thread_local.staticmethod_context = self.old_context
