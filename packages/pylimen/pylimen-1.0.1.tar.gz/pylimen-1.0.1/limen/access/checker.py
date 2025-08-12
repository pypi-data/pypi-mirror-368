"""
Main access checking logic
"""
from typing import Type
from ..core import AccessLevel, InheritanceType, CallerInfo
from ..inspection import StackInspector
from .friendship import FriendshipManager
from .inheritance import InheritanceAnalyzer


class AccessChecker:
    """Main access checking logic"""
    
    def __init__(self, friendship_manager: FriendshipManager, 
                 inheritance_analyzer: InheritanceAnalyzer,
                 stack_inspector: StackInspector):
        self._friendship_manager = friendship_manager
        self._inheritance_analyzer = inheritance_analyzer
        self._stack_inspector = stack_inspector
    
    def can_access(self, target_class: Type, method_name: str, 
                   access_level: AccessLevel, caller_info: CallerInfo = None, 
                   instance_class: Type = None) -> bool:
        """Check if access should be allowed"""
        if not caller_info:
            caller_info = self._stack_inspector.get_caller_info()
        
        caller_class = caller_info.caller_class
        
        # Check for friend access first (unified logic)
        if self._check_friend_access(target_class, access_level, caller_info):
            return True
        
        # Use instance class if provided for inheritance analysis
        actual_target_class = instance_class if instance_class else target_class
        
        # Same class access is always allowed
        if caller_class == target_class:
            return True
        
        # Check if this is inheritance access (caller is derived from target)
        if caller_class and target_class and issubclass(caller_class, target_class):
            inheritance_type = self._inheritance_analyzer.get_inheritance_type(caller_class, target_class)
            
            # For private inheritance, derived class can still access protected/public methods internally
            if inheritance_type == InheritanceType.PRIVATE:
                # Allow internal access to protected and public methods
                if access_level in [AccessLevel.PROTECTED, AccessLevel.PUBLIC]:
                    return True
                # Private methods are never accessible even with inheritance
                return False
            
            # For protected inheritance, allow access to protected and public methods
            elif inheritance_type == InheritanceType.PROTECTED:
                if access_level in [AccessLevel.PROTECTED, AccessLevel.PUBLIC]:
                    return True
                return False
                
            # For public inheritance (normal inheritance), follow normal protected rules
            elif inheritance_type == InheritanceType.PUBLIC:
                if access_level == AccessLevel.PUBLIC:
                    return True
                elif access_level == AccessLevel.PROTECTED:
                    return True
                return False
        
        # Get effective access level considering inheritance (for external access to derived objects)
        effective_access = self._inheritance_analyzer.get_inherited_access_level(
            actual_target_class, method_name, access_level, caller_class
        )
        
        return self._check_access_by_level(effective_access, target_class, caller_class, caller_info)
    
    def _check_friend_access(self, target_class: Type, access_level: AccessLevel, caller_info: CallerInfo) -> bool:
        """Unified friend access checking logic"""
        # Only check friends for private and protected access
        if access_level not in [AccessLevel.PRIVATE, AccessLevel.PROTECTED]:
            return False
        
        caller_class = caller_info.caller_class
        caller_method = caller_info.caller_method
        
        # Additional check: Look for friend attributes on the caller function itself
        # This handles cases where friend functions are wrapped in standard descriptors
        if caller_class and caller_method:
            try:
                caller_func = getattr(caller_class, caller_method, None)
                if caller_func:
                    # Extract the actual function from various descriptor types
                    actual_func = self._extract_function_from_descriptor(caller_func)
                    
                    # Check if the actual function has friend attributes
                    if (actual_func and 
                        hasattr(actual_func, '_limen_friend_target') and
                        hasattr(actual_func, '_limen_is_friend_method') and
                        actual_func._limen_friend_target is target_class):
                        return True
            except (AttributeError, TypeError):
                pass
        
        # If normal stack inspection didn't find a caller class, check thread-local staticmethod context
        if caller_class is None:
            try:
                from ..descriptors.static_method import _thread_local
                staticmethod_context = getattr(_thread_local, 'staticmethod_context', None)
                if staticmethod_context:
                    caller_class = staticmethod_context['caller_class']
                    caller_method = staticmethod_context['caller_method']
            except (ImportError, AttributeError):
                pass
        
        if not caller_method:
            return False
        
        # Check for friend function access (when caller_class is None)
        if caller_class is None:
            # Check if it's a friend function
            if self._friendship_manager.is_friend_function(target_class, caller_method):
                return True
            
            # Also check for staticmethod friend access (staticmethods have caller_class = None)
            if self._friendship_manager.is_staticmethod_friend(target_class, caller_method):
                return True
        else:
            # Check for friend method access (when caller_class is not None)
            if self._friendship_manager.is_friend_method(target_class, caller_class, caller_method):
                return True
            
            # Check for friend class access
            if self._friendship_manager.is_friend(target_class, caller_class):
                return True
        
        return False
    
    def _extract_function_from_descriptor(self, descriptor):
        """Extract the underlying function from various descriptor types"""
        from ..utils.descriptors import extract_function_from_descriptor
        return extract_function_from_descriptor(descriptor)

    def _check_access_by_level(self, access_level: AccessLevel, 
                              target_class: Type, caller_class: Type, caller_info: CallerInfo = None) -> bool:
        """Check access based on access level using unified strategy pattern"""
        # Unified access level checking strategy
        access_strategies = {
            AccessLevel.PUBLIC: lambda: True,
            AccessLevel.PRIVATE: lambda: self._check_private_access(target_class, caller_class, caller_info),
            AccessLevel.PROTECTED: lambda: self._check_protected_access(target_class, caller_class, caller_info)
        }
        
        strategy = access_strategies.get(access_level)
        return strategy() if strategy else False
    
    def _check_private_access(self, target_class: Type, caller_class: Type, caller_info: CallerInfo = None) -> bool:
        """Check private access (same class only - friends already checked in can_access)"""
        # Private methods are only accessible from same class (if caller_class exists)
        return caller_class == target_class if caller_class else False
    
    def _check_protected_access(self, target_class: Type, caller_class: Type, caller_info: CallerInfo = None) -> bool:
        """Check protected access (inheritance hierarchy - friends already checked in can_access)"""        
        if not caller_class:
            return False
        
        # Check inheritance access
        if issubclass(caller_class, target_class) or issubclass(target_class, caller_class):
            if issubclass(caller_class, target_class):
                inheritance_type = self._inheritance_analyzer.get_inheritance_type(
                    caller_class, target_class
                )
                return inheritance_type in [InheritanceType.PUBLIC, InheritanceType.PROTECTED]
            return True
        
        return False
