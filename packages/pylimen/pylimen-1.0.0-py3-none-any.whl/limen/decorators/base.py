"""
Base class for access control decorators using Template Method pattern
"""
import inspect
from ..core import AccessLevel, InheritanceType
from ..descriptors import DescriptorFactory


class AccessControlDecorator:
    """Base class for access control decorators using Template Method pattern"""
    
    def __init__(self, access_level: AccessLevel):
        self._access_level = access_level
    
    def __call__(self, *args):
        """Template method for decorator application"""
        if len(args) == 0:
            return self._create_parameterized_decorator()
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, type):
                # This is a class - we need to check if it's bare decoration or inheritance
                if self._is_bare_class_decoration():
                    # This is bare decoration like @private \n class Foo:
                    # Apply implicit access control based on naming conventions
                    return self._handle_implicit_class_decoration(arg)
                else:
                    # This is valid - @private(BaseClass) called, now applying to derived class
                    return self._handle_class_decoration(arg)
            else:
                return self._apply_to_function(arg)
        else:
            return self._handle_multiple_arguments(args)
    
    def _create_parameterized_decorator(self):
        """Create decorator when called with parentheses"""
        def decorator(func):
            return self._apply_to_function(func)
        return decorator
    
    def _handle_multiple_arguments(self, args):
        """Handle multiple arguments (inheritance from multiple bases)"""
        if all(isinstance(arg, type) for arg in args):
            return self._create_inheritance_decorator(args)
        else:
            raise ValueError(f"All arguments to @{self._access_level.value} must be classes for inheritance")
    
    def _apply_to_function(self, func):
        """Apply access control to a function"""
        self._validate_function_usage(func)
        self._check_access_level_conflict(func)
        
        # Check if this is already a descriptor created by the bouncer system
        from ..descriptors.base import AccessControlledDescriptor
        if isinstance(func, AccessControlledDescriptor):
            # Update the access level of the existing descriptor
            func._access_level = self._access_level
            return func
        
        return DescriptorFactory.create_method_descriptor(func, self._access_level)
    
    def _handle_implicit_class_decoration(self, cls):
        """Handle bare class decoration (should raise error for now)"""
        # For now, we don't support bare class decoration like @private \n class Foo:
        # This would be for implicit access control on the class itself
        # But the user's requirements show this should be an error case
        raise ValueError(
            f"@{self._access_level.value} cannot be used as a class decorator without arguments. "
            f"Use @{self._access_level.value}(BaseClass) for inheritance, or apply the decorator to individual methods."
        )
    
    def _handle_class_decoration(self, cls):
        """Handle class decoration (inheritance)"""
        # If we get here, it's valid inheritance decoration
        return self._create_inheritance_decorator([cls])
    
    def _create_inheritance_decorator(self, base_classes):
        """Create inheritance decorator"""
        inheritance_type = InheritanceType(self._access_level.value)
        
        def decorator(derived_class):
            # Validate that this is actually being applied to a class
            if not isinstance(derived_class, type):
                base_names = [base.__name__ for base in base_classes]
                if callable(derived_class):
                    if hasattr(derived_class, '__qualname__') and '.' in derived_class.__qualname__:
                        target_type = "method"
                    else:
                        target_type = "function"
                    raise ValueError(
                        f"@{self._access_level.value}({', '.join(base_names)}) cannot be applied to {target_type}. "
                        f"Inheritance decorators can only be applied to classes. "
                        f"Use @{self._access_level.value} (without parentheses) for {target_type} access control."
                    )
                else:
                    raise ValueError(
                        f"@{self._access_level.value}({', '.join(base_names)}) can only be applied to classes for inheritance."
                    )
            
            # Apply implicit access control to base classes first
            for base_class in base_classes:
                self._apply_implicit_access_control(base_class)
            
            # Then apply to derived class
            self._apply_implicit_access_control(derived_class)
            
            if not hasattr(derived_class, '_inheritance_info'):
                derived_class._inheritance_info = {}
            
            for base_class in base_classes:
                derived_class._inheritance_info[base_class.__name__] = inheritance_type.value
                # Additional inheritance logic would go here
            
            return derived_class
        
        return decorator
    
    def _validate_function_usage(self, func):
        """Validate decorator is used on class methods"""
        from ..utils.validation import validate_method_usage
        validate_method_usage(func, self._access_level.value)

    def _check_access_level_conflict(self, func):
        """Check for conflicting access level decorators"""
        from ..utils.descriptors import (
            get_access_level_from_descriptor, 
            get_friend_flag_from_descriptor,
            get_wrapper_info_from_descriptor
        )
        from ..utils.error_messages import format_decorator_conflict_message
        
        existing_level = get_access_level_from_descriptor(func)
        has_friend_flag = get_friend_flag_from_descriptor(func)

        if existing_level is not None:
            # Special case: Allow overriding or confirming access level if it was set by friend decorator
            if has_friend_flag and existing_level == AccessLevel.PUBLIC:
                # Allow explicit access level to override or confirm the friend decorator's default
                return
            
            # Provide more specific error messages based on the wrapper type
            wrapper_info = get_wrapper_info_from_descriptor(func)
            
            error_message = format_decorator_conflict_message(
                existing_level.value, self._access_level.value, 
                getattr(func, '__name__', 'unknown'), wrapper_info
            )
            raise ValueError(error_message)

    def _is_bare_class_decoration(self):
        """Check if this is bare class decoration (invalid)"""
        try:
            # Use inspect.stack() to get reliable frame information
            stack = inspect.stack()
            
            # Look for the decorator application in the stack
            # We skip the first few frames which are internal to our decorator
            for frame_info in stack[3:8]:  # Check a reasonable range of frames
                if frame_info.code_context:
                    line = frame_info.code_context[0].strip()
                    # Look for patterns like "@private" without parentheses
                    decorator_name = f"@{self._access_level.value}"
                    if line.startswith(decorator_name) and "(" not in line:
                        return True  # Bare decoration detected
                    elif f"@{self._access_level.value}(" in line:
                        return False  # Inheritance decoration detected
            
            # If we can't determine from the stack, assume it's valid (safer)
            return False
        except Exception:
            # If anything goes wrong with stack inspection, assume valid
            return False
    
    def _apply_implicit_access_control(self, cls):
        """Apply implicit access control based on naming conventions and inheritance"""
        from ..utils import apply_implicit_access_control
        from ..descriptors import DescriptorFactory
        
        # First apply standard implicit access control
        apply_implicit_access_control(cls)
        
        # For inheritance decoration, also ensure all inherited methods have descriptors
        # so they can participate in inheritance-based access control
        for name in dir(cls):
            # Skip special methods and private attributes
            if name.startswith('__') and name.endswith('__'):
                continue
            if name.startswith('_' + cls.__name__ + '__'):  # Name-mangled private
                continue
                
            attr = getattr(cls, name)
            
            # Only process callable methods that aren't already our descriptors
            if (callable(attr) and 
                not hasattr(attr, '_access_level') and 
                not hasattr(attr, '_owner')):
                
                # Check if this method is inherited (not defined in this class)
                if name not in cls.__dict__:
                    # This is an inherited method - wrap it with a descriptor
                    # so it can participate in inheritance-based access control
                    
                    # Determine the original access level
                    if name.startswith('_'):
                        access_level = AccessLevel.PROTECTED
                    else:
                        access_level = AccessLevel.PUBLIC
                    
                    # Create a descriptor for the inherited method
                    descriptor = DescriptorFactory.create_method_descriptor(attr, access_level)
                    setattr(cls, name, descriptor)
                    if hasattr(descriptor, '__set_name__'):
                        descriptor.__set_name__(cls, name)
