"""
Custom exception classes for the Limen Access Control System
"""


class AccessControlError(Exception):
    """Base exception for access control errors"""
    pass


class PermissionDeniedError(AccessControlError):
    """Raised when access to a method or property is denied"""
    
    def __init__(self, access_level: str, member_type: str, member_name: str):
        self.access_level = access_level
        self.member_type = member_type
        self.member_name = member_name
        super().__init__(f"Access denied to {access_level} {member_type} {member_name}")


class DecoratorConflictError(AccessControlError):
    """Raised when conflicting access level decorators are applied"""
    
    def __init__(self, existing_level: str, new_level: str, method_name: str):
        self.existing_level = existing_level
        self.new_level = new_level
        self.method_name = method_name
        super().__init__(
            f"Conflicting access level decorators on {method_name}: "
            f"already has @{existing_level} decorator, cannot apply @{new_level} decorator"
        )


class InvalidDecoratorUsageError(AccessControlError):
    """Raised when decorators are used incorrectly"""
    pass


class FriendshipError(AccessControlError):
    """Raised when there are issues with friend relationships"""
    pass
