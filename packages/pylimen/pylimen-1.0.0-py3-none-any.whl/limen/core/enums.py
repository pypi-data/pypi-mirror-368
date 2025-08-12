"""
Core enums for the Bouncer Access Control System
"""
from enum import Enum


class AccessLevel(Enum):
    """Enum for access control levels"""
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"


class InheritanceType(Enum):
    """Enum for inheritance types"""
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
