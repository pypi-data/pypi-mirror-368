"""
Protocol definitions for the Limen Access Control System
"""
from typing import Type, Protocol, runtime_checkable
from .enums import AccessLevel, InheritanceType
from .value_objects import CallerInfo


@runtime_checkable
class IAccessChecker(Protocol):
    """Interface for access checking strategies"""
    
    def can_access(self, target_class: Type, method_name: str, 
                   access_level: AccessLevel, caller_info: CallerInfo) -> bool:
        """Check if access should be allowed"""
        ...


@runtime_checkable
class IEventEmitter(Protocol):
    """Interface for event emission"""
    
    def emit(self, event_type: str, data: dict) -> None:
        """Emit an event"""
        ...


@runtime_checkable
class IStackInspector(Protocol):
    """Interface for stack inspection"""
    
    def get_caller_info(self) -> CallerInfo:
        """Get caller information from stack"""
        ...
    
    def is_explicit_base_class_call(self, target_class: Type, caller_class: Type) -> bool:
        """Check if this is an explicit Base.method() call"""
        ...


@runtime_checkable
class IFriendshipManager(Protocol):
    """Interface for managing friend relationships"""
    
    def register_friend(self, target_class: Type, friend_class: Type) -> None:
        """Register a friend relationship"""
        ...
    
    def is_friend(self, target_class: Type, caller_class: Type) -> bool:
        """Check if caller is a friend of target"""
        ...


@runtime_checkable
class IInheritanceAnalyzer(Protocol):
    """Interface for inheritance analysis"""
    
    def get_inheritance_type(self, derived_class: Type, base_class: Type) -> InheritanceType:
        """Get the inheritance type between classes"""
        ...
    
    def get_inherited_access_level(self, target_class: Type, method_name: str, 
                                  original_access: AccessLevel, caller_class: Type) -> AccessLevel:
        """Determine effective access level for inherited methods"""
        ...
