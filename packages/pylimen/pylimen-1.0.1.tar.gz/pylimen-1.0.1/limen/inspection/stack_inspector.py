"""
Stack inspection logic for the Limen Access Control System
"""
import inspect
from typing import Type
from ..core import CallerInfo


class StackInspector:
    """Handles stack inspection logic"""
    
    PYTEST_MODULES = ['pluggy', '_pytest', 'pytest', 'unittest', 'runpy', 'importlib']
    WRAPPER_FUNCTIONS = [
        'controlled_static', 'controlled_class', 'wrapper',
        'static_wrapper', 'class_wrapper', 'method_wrapper',
        'controlled_getattribute', 'controlled_setattr', 'getter',
        '_check_access', '__get__', '__set__', '__delete__',  # Add descriptor methods
        'can_access'  # Add access checker method
    ]
    
    def _get_staticmethod_context(self):
        """Get staticmethod context from thread-local storage"""
        try:
            from ..descriptors.static_method import _thread_local
            return getattr(_thread_local, 'staticmethod_context', None)
        except ImportError:
            return None
    
    def get_caller_info(self) -> CallerInfo:
        """Get caller class and method from stack"""
        stack = inspect.stack()
        
        # Look for caller starting from frame 1 (to catch wrapper functions)
        for i, frame_info in enumerate(stack[1:], 1):
            frame_locals = frame_info.frame.f_locals
            
            # Skip limen internal frames first
            if self._is_internal_frame(frame_info):
                continue
            
            # Look for instance methods (with 'self')
            if 'self' in frame_locals:
                caller_instance = frame_locals['self']
                caller_method_name = frame_info.function
                caller_class = self._find_method_defining_class(
                    caller_instance, caller_method_name
                )
                return CallerInfo(caller_class, caller_method_name)
            
            # Look for class methods (with 'cls')
            elif 'cls' in frame_locals:
                caller_class = frame_locals['cls']
                caller_method_name = frame_info.function
                # For classmethods, the class is directly available
                if isinstance(caller_class, type):
                    return CallerInfo(caller_class, caller_method_name)
            
            # Look for standalone functions (no 'self' or 'cls')
            else:
                function_name = frame_info.function
                
                # Check if this is a static method by examining qualname
                frame_globals = frame_info.frame.f_globals
                if function_name in frame_globals:
                    func = frame_globals[function_name]
                    if hasattr(func, '__qualname__') and '.' in func.__qualname__:
                        # This might be a static method - extract class name
                        qualname_parts = func.__qualname__.split('.')
                        if len(qualname_parts) >= 2:
                            class_name = qualname_parts[-2]  # Second-to-last part should be class name
                            # Try to find the class in globals
                            if class_name in frame_globals:
                                potential_class = frame_globals[class_name]
                                if isinstance(potential_class, type):
                                    # Check if this function is actually a static method of this class
                                    if hasattr(potential_class, function_name):
                                        class_attr = getattr(potential_class, function_name)
                                        if isinstance(class_attr, staticmethod):
                                            return CallerInfo(potential_class, function_name)
                
                return CallerInfo(None, function_name)
        
        # Fallback: check thread-local staticmethod context
        staticmethod_context = self._get_staticmethod_context()
        if staticmethod_context:
            return CallerInfo(
                caller_class=staticmethod_context['caller_class'],
                caller_method=staticmethod_context['caller_method']
            )
        
        return CallerInfo(None, None)
    
    def is_explicit_base_class_call(self, target_class: Type, caller_class: Type) -> bool:
        """Detect if this is an explicit Base.method() call vs inherited access"""
        stack = inspect.stack()
        
        for frame_info in stack[3:]:
            if self._is_internal_frame(frame_info):
                continue
            
            code_context = frame_info.code_context
            if code_context:
                for line in code_context:
                    if line and f"{target_class.__name__}." in line:
                        return True
            break
        
        return False
    
    def _is_internal_frame(self, frame_info) -> bool:
        """Check if frame is internal (pytest or limen)"""
        return (self._is_pytest_internal_frame(frame_info) or 
                self._is_limen_wrapper_frame(frame_info))
    
    def _is_pytest_internal_frame(self, frame_info) -> bool:
        """Check if a frame is part of pytest's internal execution"""
        filename = frame_info.filename
        module_name = frame_info.frame.f_globals.get('__name__', '')
        
        return any(pytest_module in module_name or pytest_module in filename 
                  for pytest_module in self.PYTEST_MODULES)
    
    def _is_limen_wrapper_frame(self, frame_info) -> bool:
        """Check if a frame is one of our wrapper functions"""
        return frame_info.function in self.WRAPPER_FUNCTIONS
    
    def _find_method_defining_class(self, instance, method_name) -> Type:
        """Find the class that actually defines the given method"""
        instance_class = type(instance)
        
        for cls in instance_class.__mro__:
            if hasattr(cls, method_name) and method_name in cls.__dict__:
                return cls
        
        return instance_class
