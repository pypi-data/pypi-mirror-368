"""
Value objects for the Limen Access Control System
"""
from typing import Type, Optional


class CallerInfo:
    """Value object to hold caller information"""
    
    def __init__(self, caller_class: Optional[Type], caller_method: Optional[str]):
        self.caller_class = caller_class
        self.caller_method = caller_method
    
    def __bool__(self):
        return self.caller_class is not None
    
    def __repr__(self):
        return f"CallerInfo(caller_class={self.caller_class}, caller_method={self.caller_method})"
    
    def __eq__(self, other):
        if not isinstance(other, CallerInfo):
            return False
        return (self.caller_class == other.caller_class and 
                self.caller_method == other.caller_method)
