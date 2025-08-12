"""
Method information extraction utilities for exception handling
"""
import inspect
import textwrap
from typing import Tuple, List, Optional, Any


class MethodInspector:
    """Utility class for extracting method information from function objects"""
    
    @staticmethod
    def extract_method_info(func_obj: Any) -> Tuple[str, str, List[str]]:
        """Extract method type, arguments, and wrapper decorators from a function object
        
        Returns:
            Tuple of (method_type, arguments, wrapper_decorators)
        """
        method_type = 'method'
        arguments = 'self'
        wrapper_decorators = []
        original_func = func_obj
        
        try:
            # Check for wrapper decorators and unwrap
            if isinstance(func_obj, property):
                wrapper_decorators.append('property')
                method_type = 'property'
                original_func = func_obj.fget
            elif isinstance(func_obj, staticmethod):
                wrapper_decorators.append('staticmethod')
                method_type = 'staticmethod'
                original_func = func_obj.__func__
            elif isinstance(func_obj, classmethod):
                wrapper_decorators.append('classmethod')
                method_type = 'classmethod'
                original_func = func_obj.__func__
            
            # Try to unwrap further for access control descriptors
            original_func = MethodInspector._unwrap_access_control_descriptor(original_func)
            
            # Get function signature
            if original_func and callable(original_func):
                try:
                    arguments, return_annotation = MethodInspector._extract_signature_info(original_func)
                    method_type = MethodInspector._determine_method_type(original_func, method_type, wrapper_decorators)
                    
                    # Store return annotation for later use (this is a bit of a hack, but maintains compatibility)
                    if hasattr(func_obj, '_limen_return_annotation'):
                        func_obj._limen_return_annotation = return_annotation
                        
                except Exception:
                    # Fallback to basic code inspection
                    arguments, method_type = MethodInspector._fallback_code_inspection(original_func, method_type)
                    
        except Exception:
            # Ultimate fallback - use defaults
            pass
            
        return method_type, arguments, wrapper_decorators
    
    @staticmethod
    def _unwrap_access_control_descriptor(func: Any) -> Any:
        """Unwrap access control descriptors to get to the original function"""
        if hasattr(func, '_func_or_value'):
            return func._func_or_value
        elif hasattr(func, '_original_func'):
            return func._original_func
        elif hasattr(func, '__wrapped__'):
            return func.__wrapped__
        return func
    
    @staticmethod
    def _extract_signature_info(func: Any) -> Tuple[str, str]:
        """Extract signature and return annotation from function"""
        sig = inspect.signature(func)
        
        # Build arguments with type hints if available
        param_strings = []
        for param in sig.parameters.values():
            param_str = param.name
            
            # Add type annotation if present
            if param.annotation != inspect.Parameter.empty:
                if hasattr(param.annotation, '__name__'):
                    param_str += f": {param.annotation.__name__}"
                else:
                    param_str += f": {param.annotation}"
            
            # Add default value if present
            if param.default != inspect.Parameter.empty:
                if isinstance(param.default, str):
                    param_str += f" = '{param.default}'"
                else:
                    param_str += f" = {param.default}"
            
            param_strings.append(param_str)
        
        arguments = ', '.join(param_strings)
        
        # Add return type annotation if present
        return_annotation = ""
        if sig.return_annotation != inspect.Signature.empty:
            if hasattr(sig.return_annotation, '__name__'):
                return_annotation = f" -> {sig.return_annotation.__name__}"
            else:
                return_annotation = f" -> {sig.return_annotation}"
        
        return arguments, return_annotation
    
    @staticmethod
    def _determine_method_type(func: Any, current_type: str, wrapper_decorators: List[str]) -> str:
        """Determine the actual method type based on parameters"""
        try:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            if not params:
                if current_type in ['staticmethod']:
                    return current_type
                else:
                    return 'function'
            elif params[0] == 'self' and current_type == 'method':
                return 'method'
            elif params[0] == 'cls' and current_type in ['method', 'classmethod']:
                if 'classmethod' not in wrapper_decorators:
                    wrapper_decorators.append('classmethod')
                return 'classmethod'
            elif current_type in ['staticmethod', 'property']:
                return current_type
            else:
                return 'function'
        except Exception:
            return current_type
    
    @staticmethod
    def _fallback_code_inspection(func: Any, method_type: str) -> Tuple[str, str]:
        """Fallback method using code object inspection"""
        if hasattr(func, '__code__'):
            code = func.__code__
            arg_count = code.co_argcount
            var_names = code.co_varnames[:arg_count]
            
            if var_names:
                arguments = ', '.join(var_names)
                if var_names[0] == 'self':
                    method_type = method_type if method_type != 'method' else 'method'
                elif var_names[0] == 'cls':
                    method_type = 'classmethod'
                elif method_type == 'staticmethod':
                    pass  # Keep staticmethod
                else:
                    method_type = 'function'
            else:
                arguments = ''
                method_type = 'function' if method_type == 'method' else method_type
        else:
            arguments = 'self'
            
        return arguments, method_type


class FunctionBodyExtractor:
    """Utility class for extracting function implementation bodies"""
    
    @staticmethod
    def extract_function_body(func_obj: Any) -> str:
        """Extract the actual implementation body of the function"""
        try:
            # Unwrap to get to the original function
            original_func = FunctionBodyExtractor._unwrap_function(func_obj)
            
            if original_func and callable(original_func):
                source_lines = FunctionBodyExtractor._get_source_lines(original_func)
                if source_lines:
                    return FunctionBodyExtractor._process_function_body(source_lines)
                
        except Exception:
            # Fallback to generic implementation
            pass
        
        return "    pass"
    
    @staticmethod
    def _unwrap_function(func_obj: Any) -> Any:
        """Unwrap function to get to the original implementation"""
        original_func = func_obj
        
        if isinstance(func_obj, property):
            original_func = func_obj.fget
        elif isinstance(func_obj, (staticmethod, classmethod)):
            original_func = func_obj.__func__
        
        # Try to unwrap further for access control descriptors
        if hasattr(original_func, '_func_or_value'):
            original_func = original_func._func_or_value
        elif hasattr(original_func, '_original_func'):
            original_func = original_func._original_func
        elif hasattr(original_func, '__wrapped__'):
            original_func = original_func.__wrapped__
            
        return original_func
    
    @staticmethod
    def _get_source_lines(func: Any) -> Optional[List[str]]:
        """Get source lines for a function"""
        try:
            source_lines, start_line = inspect.getsourcelines(func)
            return source_lines
        except Exception:
            return None
    
    @staticmethod
    def _process_function_body(source_lines: List[str]) -> str:
        """Process source lines to extract function body"""
        # Find the line with the function definition (contains 'def')
        func_def_index = -1
        for i, line in enumerate(source_lines):
            if line.strip().startswith('def ') and ':' in line:
                func_def_index = i
                break
        
        if func_def_index >= 0 and func_def_index + 1 < len(source_lines):
            # Get the body lines (everything after the def line)
            body_lines = source_lines[func_def_index + 1:]
            
            if body_lines:
                # Join and clean up the body
                body = ''.join(body_lines)
                dedented_body = textwrap.dedent(body)
                
                if dedented_body.strip():
                    # Re-indent to 4 spaces
                    indented_body = textwrap.indent(dedented_body.strip(), '    ')
                    
                    # Limit to reasonable length (first 6 lines max)
                    lines = indented_body.split('\n')
                    if len(lines) > 6:
                        lines = lines[:6] + ['    # ... (truncated)']
                    
                    return '\n'.join(lines)
        
        return "    pass"


class TargetFormatter:
    """Utility class for formatting target names in error messages"""
    
    @staticmethod
    def format_target_name(method_name: str, method_type: str = 'method') -> str:
        """Format the target name appropriately based on method type"""
        if method_type == 'property':
            return method_name
        else:
            return f"{method_name}()"
    
    @staticmethod
    def format_qualified_target(class_name: str, method_name: str, method_type: str = 'method') -> str:
        """Format a fully qualified target name"""
        target_name = TargetFormatter.format_target_name(method_name, method_type)
        return f"{class_name}.{target_name}"
