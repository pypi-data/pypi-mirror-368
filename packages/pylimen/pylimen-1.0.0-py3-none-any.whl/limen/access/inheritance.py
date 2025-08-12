"""
Analyzes inheritance relationships and types
"""
from typing import Type
from ..core import AccessLevel, InheritanceType


class InheritanceAnalyzer:
    """Analyzes inheritance relationships and types"""
    
    def get_inheritance_type(self, derived_class: Type, base_class: Type) -> InheritanceType:
        """Get the inheritance type between classes"""
        if hasattr(derived_class, '_inheritance_info'):
            base_name = base_class.__name__
            inheritance_str = derived_class._inheritance_info.get(
                base_name, InheritanceType.PUBLIC.value
            )
            return InheritanceType(inheritance_str)
        return InheritanceType.PUBLIC
    
    def get_inherited_access_level(self, target_class: Type, method_name: str, 
                                  original_access: AccessLevel, caller_class: Type) -> AccessLevel:
        """Determine effective access level for inherited methods"""
        # Handle None method name gracefully (can happen during descriptor initialization)
        if method_name is None:
            return original_access
            
        for base_class in target_class.__mro__[1:]:
            if hasattr(base_class, method_name):
                inheritance_type = self.get_inheritance_type(target_class, base_class)
                
                if inheritance_type == InheritanceType.PRIVATE:
                    if original_access in [AccessLevel.PUBLIC, AccessLevel.PROTECTED]:
                        if caller_class is None:
                            return AccessLevel.PRIVATE
                        elif not self._is_same_or_derived_class(target_class, caller_class):
                            return AccessLevel.PRIVATE
                
                elif inheritance_type == InheritanceType.PROTECTED:
                    if original_access == AccessLevel.PUBLIC:
                        if caller_class is None:
                            return AccessLevel.PROTECTED
                        elif not self._is_in_inheritance_hierarchy(target_class, caller_class):
                            return AccessLevel.PROTECTED
                
                break
        
        return original_access
    
    def _is_same_or_derived_class(self, target_class: Type, caller_class: Type) -> bool:
        """Check if caller is the target class itself or derived from it"""
        return caller_class == target_class or issubclass(caller_class, target_class)
    
    def _is_in_inheritance_hierarchy(self, target_class: Type, caller_class: Type) -> bool:
        """Check if classes are in the same inheritance hierarchy"""
        return (issubclass(caller_class, target_class) or 
                issubclass(target_class, caller_class))
