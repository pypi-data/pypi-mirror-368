"""
Access control decorators (private, protected, public)
"""
from ..core import AccessLevel
from .base import AccessControlDecorator


def private(*args):
    """@private decorator for methods and classes"""
    decorator = AccessControlDecorator(AccessLevel.PRIVATE)
    return decorator(*args)


def protected(*args):
    """@protected decorator for methods and classes"""
    decorator = AccessControlDecorator(AccessLevel.PROTECTED)
    return decorator(*args)


def public(*args):
    """@public decorator for methods and classes"""
    decorator = AccessControlDecorator(AccessLevel.PUBLIC)
    return decorator(*args)
