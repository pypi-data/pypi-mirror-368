"""
Unified error message generation utilities
"""
from typing import Optional
from ..core import AccessLevel


def format_access_denied_message(access_level: AccessLevel, member_type: str, 
                                member_name: str, caller_class: Optional[str] = None) -> str:
    """Generate consistent access denied messages"""
    caller_info = f" from {caller_class}" if caller_class else ""
    return f"Access denied to {access_level.value} {member_type} '{member_name}'{caller_info}"


def format_decorator_conflict_message(existing_level: str, new_level: str, 
                                    method_name: str, wrapper_info: str = "") -> str:
    """Generate consistent decorator conflict messages"""
    if existing_level == new_level:
        return (
            f"Duplicate access level decorators: method '{method_name}' already has @{existing_level} "
            f"decorator{wrapper_info}, cannot apply another @{new_level} decorator"
        )
    else:
        return (
            f"Conflicting access level decorators: method '{method_name}' already has @{existing_level} "
            f"decorator{wrapper_info}, cannot apply @{new_level} decorator"
        )


def format_invalid_usage_message(decorator_name: str, context: str) -> str:
    """Generate consistent invalid usage messages"""
    return (
        f"@{decorator_name} decorator cannot be applied to {context}. "
        f"Access control decorators can only be used on class methods."
    )


def format_bare_class_decoration_message(decorator_name: str) -> str:
    """Generate consistent bare class decoration error messages"""
    return (
        f"@{decorator_name} cannot be used as a class decorator without arguments. "
        f"Use @{decorator_name}(BaseClass) for {decorator_name} inheritance from BaseClass, "
        f"or apply @{decorator_name} to individual methods instead."
    )
