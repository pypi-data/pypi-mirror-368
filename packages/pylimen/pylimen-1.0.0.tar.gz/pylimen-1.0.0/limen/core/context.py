"""
Thread-local context management for performance optimization
"""
import threading
from contextlib import contextmanager


# Thread-local storage for performance optimization
_call_context = threading.local()


@contextmanager
def internal_call_context():
    """Context manager to avoid repeated stack inspection for internal calls"""
    already_in_context = hasattr(_call_context, 'in_internal_call')
    if not already_in_context:
        _call_context.in_internal_call = True
    try:
        yield
    finally:
        if not already_in_context:
            delattr(_call_context, 'in_internal_call')


def is_in_internal_call() -> bool:
    """Check if we're currently in an internal call context"""
    return hasattr(_call_context, 'in_internal_call')
