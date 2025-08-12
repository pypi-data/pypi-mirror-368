"""
Implicit access control based on naming conventions
"""
from typing import Type, Set
from ..descriptors import DescriptorFactory
from .naming import detect_implicit_access_level


def install_name_mangling_protection(cls: Type, private_methods: Set[str]) -> None:
    """
    Install protection against name mangling bypasses for private methods.
    Only applies to mangled names that correspond to actual private methods.
    """
    def protected_getattribute(self, name):
        """Custom __getattribute__ that prevents name mangling bypasses"""
        # Check if this is a mangled private method access (_ClassName__method)
        if name.startswith(f'_{cls.__name__}__'):
            # Extract the original method name (__method)
            original_name = '__' + name[len(f'_{cls.__name__}__'):]
            
            # Only apply protection if this corresponds to a tracked private method
            if original_name in private_methods:
                # Import here to avoid circular imports
                from ..system.access_control import get_access_control_system
                from ..inspection.stack_inspector import StackInspector
                from ..core import AccessLevel
                
                access_control = get_access_control_system()
                
                # If enforcement is disabled, allow access
                if not access_control.enforcement_enabled:
                    return object.__getattribute__(self, name)
                
                # Get caller info
                stack_inspector = StackInspector()
                caller_info = stack_inspector.get_caller_info()
                
                # Check if access should be allowed
                if hasattr(access_control, '_access_checker'):
                    result = access_control._access_checker.can_access(
                        cls, original_name, AccessLevel.PRIVATE, caller_info, self.__class__
                    )
                else:
                    result = access_control.check_access(cls, original_name, AccessLevel.PRIVATE)
                
                if not result:
                    raise PermissionError(
                        f"Access denied to private method {original_name} via name mangling bypass"
                    )
        
        # Default behavior - use object.__getattribute__ to avoid conflicts
        return object.__getattribute__(self, name)
    
    # Install the protected __getattribute__ method
    cls.__getattribute__ = protected_getattribute


def apply_implicit_access_control(cls: Type) -> None:
    """
    Apply implicit access control based on naming conventions to a class.
    Only applies to methods that don't already have explicit decorators.
    """
    # Store original method names before name mangling for proper detection
    methods_to_control = {}
    private_methods = set()  # Track private methods for name mangling protection

    # Collect methods and their original names
    for name, method in list(cls.__dict__.items()):
        # Only wrap methods defined directly in this class, not inherited
        if not hasattr(cls, name):
            continue
        if getattr(getattr(cls, name), '__objclass__', cls) is not cls:
            continue
        # Skip special methods (dunder methods like __init__, __str__)
        if name.startswith('__') and name.endswith('__'):
            continue

        # Skip if already has explicit access control
        if hasattr(method, '_access_level'):
            continue

        # Skip if it's already a descriptor from our system
        if hasattr(method, '_owner') and hasattr(method, '_access_level'):
            continue

        # Handle Python name mangling: _ClassName__method -> __method
        original_name = name
        if name.startswith(f'_{cls.__name__}__'):
            # This is a name-mangled method, get the original name
            original_name = '__' + name[len(f'_{cls.__name__}__'):]

        # Detect implicit access level using original name
        implicit_level = detect_implicit_access_level(original_name)

        # Apply access control to all callable methods (including public)
        if callable(method):
            methods_to_control[name] = (method, implicit_level, original_name)
            # Track private methods for name mangling protection
            if implicit_level.value == 'private' and original_name.startswith('__'):
                private_methods.add(original_name)

    # Apply access control to methods
    for name, (method, implicit_level, original_name) in methods_to_control.items():
        # Create appropriate descriptor based on method type and access level
        if isinstance(method, staticmethod):
            descriptor = DescriptorFactory.create_static_method_descriptor(
                method.__func__, implicit_level
            )
        elif isinstance(method, classmethod):
            descriptor = DescriptorFactory.create_class_method_descriptor(
                method.__func__, implicit_level
            )
        elif isinstance(method, property):
            descriptor = DescriptorFactory.create_property_descriptor(
                method.fget, implicit_level, method.fset, method.fdel, method.__doc__
            )
        elif callable(method):
            # Regular method
            descriptor = DescriptorFactory.create_method_descriptor(method, implicit_level)
        else:
            continue

        # Replace the method with the access-controlled descriptor
        setattr(cls, name, descriptor)
        # Ensure descriptor knows its name and owner
        if hasattr(descriptor, '__set_name__'):
            descriptor.__set_name__(cls, name)

    # Install name mangling protection if we have private methods
    if private_methods:
        install_name_mangling_protection(cls, private_methods)
