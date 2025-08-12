"""
Custom exception classes for the Limen Access Control System
"""
from .message_generators import MessageGenerator


class LimenError(Exception):
    """Base exception for all Limen access control errors"""
    pass


class ContextualAccessControlError(LimenError):
    """Base class for access control errors with contextual message generation"""
    
    def __init__(self, context: dict = None):
        self.context = context or {}
        message = self._generate_contextual_message()
        super().__init__(message)
    
    def _generate_contextual_message(self) -> str:
        """Generate a contextual error message - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _generate_contextual_message")


class PermissionDeniedError(LimenError):
    """Raised when access to a method or property is denied"""
    
    def __init__(self, access_level: str, member_type: str, member_name: str):
        self.access_level = access_level
        self.member_type = member_type
        self.member_name = member_name
        super().__init__(f"Access denied to {access_level} {member_type} {member_name}")


class DecoratorConflictError(ContextualAccessControlError):
    """Raised when conflicting access level decorators are applied"""
    
    def __init__(self, existing_level: str, new_level: str, method_name: str, context: dict = None):
        self.existing_level = existing_level
        self.new_level = new_level
        self.method_name = method_name
        super().__init__(context)
    
    def _generate_contextual_message(self) -> str:
        """Generate a contextual error message with helpful suggestions"""
        return MessageGenerator.generate_conflict_message(
            self.existing_level,
            self.new_level,
            self.method_name,
            self.context
        )


class DecoratorUsageError(ContextualAccessControlError):
    """Raised when decorators are used incorrectly"""
    
    def __init__(self, decorator_name: str, usage_type: str, context: dict = None):
        self.decorator_name = decorator_name
        self.usage_type = usage_type
        super().__init__(context)
    
    def _generate_contextual_message(self) -> str:
        """Generate a contextual error message with helpful suggestions"""
        return MessageGenerator.generate_usage_error_message(
            self.decorator_name,
            self.usage_type,
            self.context
        )
