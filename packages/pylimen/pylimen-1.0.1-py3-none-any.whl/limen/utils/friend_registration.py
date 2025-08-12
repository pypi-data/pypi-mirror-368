"""
Helper functions for registering friend methods when classes are created
"""
import inspect
from typing import Type
from ..decorators.friend_decorator import _register_friend_method_if_needed


def process_class_for_friend_methods(cls: Type) -> None:
    """
    Process a class to register any friend methods that were decorated with @friend.
    This should be called whenever a class is created.
    """
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        _register_friend_method_if_needed(method, cls)
    
    # Also check class methods and static methods
    for name in dir(cls):
        attr = getattr(cls, name)
        if isinstance(attr, (classmethod, staticmethod)):
            # Get the underlying function
            if isinstance(attr, classmethod):
                _register_friend_method_if_needed(attr.__func__, cls)
            elif isinstance(attr, staticmethod):
                _register_friend_method_if_needed(attr.__func__, cls)


class FriendMethodMeta(type):
    """
    Metaclass that automatically registers friend methods when a class is created.
    """
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        process_class_for_friend_methods(cls)
        return cls
