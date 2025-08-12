"""
Centralized access control system - acts as a facade
"""
from typing import Type, Dict, Optional, Callable
from ..core import AccessLevel, InheritanceType, is_in_internal_call
from ..inspection import StackInspector
from ..access import FriendshipManager, InheritanceAnalyzer, AccessChecker
from .event_emitter import EventEmitter


class AccessControlSystem:
    """Centralized access control system - acts as a facade"""
    
    def __init__(self):
        self._method_registry: Dict[str, AccessLevel] = {}
        self._enforcement_enabled = True
        
        # Compose with specialized components
        self._friendship_manager = FriendshipManager()
        self._inheritance_analyzer = InheritanceAnalyzer()
        self._stack_inspector = StackInspector()
        self._access_checker = AccessChecker(
            self._friendship_manager, 
            self._inheritance_analyzer,
            self._stack_inspector
        )
        self._event_emitter = EventEmitter()
    
    @property
    def enforcement_enabled(self) -> bool:
        return self._enforcement_enabled
    
    @enforcement_enabled.setter
    def enforcement_enabled(self, value: bool) -> None:
        self._enforcement_enabled = value
    
    def register_friend(self, target_class: Type, friend_class: Type) -> None:
        """Register a friend class relationship"""
        self._friendship_manager.register_friend(target_class, friend_class)
    
    def register_friend_function(self, target_class: Type, friend_function: Callable) -> None:
        """Register a friend function relationship"""
        self._friendship_manager.register_friend_function(target_class, friend_function)
    
    def register_friend_method(self, target_class: Type, friend_class: Type, method_name: str) -> None:
        """Register a friend method relationship"""
        self._friendship_manager.register_friend_method(target_class, friend_class, method_name)
    
    def is_friend(self, target_class: Type, caller_class: Type) -> bool:
        """Check if caller class is a friend of target"""
        return self._friendship_manager.is_friend(target_class, caller_class)
    
    def is_friend_function(self, target_class: Type, function_name: str) -> bool:
        """Check if function is a friend of target class"""
        return self._friendship_manager.is_friend_function(target_class, function_name)
    
    def is_friend_method(self, target_class: Type, caller_class: Type, method_name: str) -> bool:
        """Check if a specific method of caller class is a friend of target class"""
        return self._friendship_manager.is_friend_method(target_class, caller_class, method_name)
    
    def register_method(self, class_name: str, method_name: str, access_level: AccessLevel) -> None:
        """Register a method's access level"""
        key = f"{class_name}.{method_name}"
        self._method_registry[key] = access_level
    
    def get_inheritance_type(self, derived_class: Type, base_class: Type) -> InheritanceType:
        """Get the inheritance type between classes"""
        return self._inheritance_analyzer.get_inheritance_type(derived_class, base_class)
    
    def check_access(self, target_class: Type, method_name: str, 
                    access_level: AccessLevel = None) -> bool:
        """Check if access should be allowed"""
        if not self._enforcement_enabled:
            return True
        
        # Performance optimization: Skip expensive stack inspection for internal calls
        if is_in_internal_call():
            return True
        
        # Get access level from registry if not provided
        if access_level is None:
            key = f"{target_class.__name__}.{method_name}"
            access_level = self._method_registry.get(key, AccessLevel.PUBLIC)
        
        return self._access_checker.can_access(target_class, method_name, access_level)
    
    def emit_event(self, event_type: str, data: dict) -> None:
        """Emit an event"""
        self._event_emitter.emit(event_type, data)
    
    def get_metrics(self) -> dict:
        """Get system metrics"""
        return {
            'total_friends': self._friendship_manager.get_friends_count(),
            'friend_relationships': self._friendship_manager.get_relationships_count(),
            'registered_methods': len(self._method_registry),
            'enforcement_enabled': self._enforcement_enabled
        }
    
    def reset(self) -> None:
        """Reset the system state"""
        self._method_registry.clear()
        self._friendship_manager.clear()
        self._enforcement_enabled = True


# Global instance using Singleton pattern
_access_control: Optional[AccessControlSystem] = None

def get_access_control_system() -> AccessControlSystem:
    """Get the global access control system (Singleton pattern)"""
    global _access_control
    if _access_control is None:
        _access_control = AccessControlSystem()
    return _access_control
