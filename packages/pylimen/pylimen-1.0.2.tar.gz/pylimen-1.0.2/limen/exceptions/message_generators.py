"""
Message generation utilities for contextual error messages
"""
from typing import Dict, List, Any
from .method_utils import MethodInspector, FunctionBodyExtractor, TargetFormatter


class MessageGenerator:
    """Utility class for generating contextual error messages"""
    
    @staticmethod
    def generate_conflict_message(
        existing_level: str,
        new_level: str, 
        method_name: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate a conflict error message"""
        func_obj = context.get('func_obj')
        
        if func_obj:
            method_type, arguments, wrapper_decorators = MethodInspector.extract_method_info(func_obj)
        else:
            method_type = 'method'
            arguments = 'self'
            wrapper_decorators = context.get('wrapper_decorators', [])
        
        if existing_level == new_level:
            return MessageGenerator._generate_duplicate_decorator_message(
                existing_level, method_name, method_type, arguments, wrapper_decorators, func_obj, context
            )
        else:
            return MessageGenerator._generate_conflicting_decorator_message(
                existing_level, new_level, method_name, method_type, arguments, wrapper_decorators, func_obj, context
            )
    
    @staticmethod
    def _generate_duplicate_decorator_message(
        decorator: str,
        method_name: str,
        method_type: str,
        arguments: str,
        wrapper_decorators: List[str],
        func_obj: Any,
        context: Dict[str, Any]
    ) -> str:
        """Generate message for duplicate decorator application"""
        return_annotation = context.get('return_annotation', '')
        function_body = FunctionBodyExtractor.extract_function_body(func_obj) if func_obj else "    pass"
        
        suggestion = MessageGenerator._build_corrected_suggestion(
            [decorator], method_name, arguments, return_annotation, function_body, wrapper_decorators
        )
        
        formatted_target = TargetFormatter.format_target_name(method_name, method_type)
        
        return (
            f"@{decorator} was applied to {formatted_target} more than once!\n"
            f"Did you mean:\n"
            f"{suggestion}\n"
            f"?"
        )
    
    @staticmethod
    def _generate_conflicting_decorator_message(
        existing_level: str,
        new_level: str,
        method_name: str,
        method_type: str,
        arguments: str,
        wrapper_decorators: List[str],
        func_obj: Any,
        context: Dict[str, Any]
    ) -> str:
        """Generate message for conflicting decorators"""
        return_annotation = context.get('return_annotation', '')
        function_body = FunctionBodyExtractor.extract_function_body(func_obj) if func_obj else "    pass"
        
        suggestion = MessageGenerator._build_corrected_suggestion(
            [new_level], method_name, arguments, return_annotation, function_body, wrapper_decorators
        )
        
        formatted_target = TargetFormatter.format_target_name(method_name, method_type)
        
        return (
            f"Conflicting access level decorators on {formatted_target}: "
            f"already has @{existing_level}, cannot apply @{new_level}.\n"
            f"Did you mean:\n"
            f"{suggestion}\n"
            f"?"
        )
    
    @staticmethod
    def generate_usage_error_message(
        decorator_name: str,
        usage_type: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate a usage error message"""
        if usage_type == "bare class":
            return MessageGenerator._generate_bare_class_message(decorator_name, context)
        elif usage_type == "module-level function":
            return MessageGenerator._generate_module_function_message(decorator_name)
        elif usage_type in ["method", "function"]:
            return MessageGenerator._generate_inheritance_syntax_error(decorator_name, usage_type)
        elif usage_type == "non-class target":
            return MessageGenerator._generate_non_class_target_message(decorator_name)
        elif usage_type == "invalid inheritance arguments":
            return MessageGenerator._generate_invalid_inheritance_message(decorator_name)
        elif usage_type == "duplicate application":
            return MessageGenerator._generate_duplicate_application_message(decorator_name, context)
        else:
            return MessageGenerator._generate_fallback_message(decorator_name, usage_type)
    
    @staticmethod
    def _generate_bare_class_message(decorator_name: str, context: Dict[str, Any]) -> str:
        """Generate message for bare class decoration error"""
        available_classes = context.get('available_classes', [])
        if available_classes:
            suggestion = f"@{decorator_name}({available_classes[0]})"
        else:
            suggestion = f"@{decorator_name}(<BaseClass>)"
        
        return (
            f"@{decorator_name} cannot be applied to a class without specifying a class to inherit from.\n"
            f"Did you mean: {suggestion} ?"
        )
    
    @staticmethod
    def _generate_module_function_message(decorator_name: str) -> str:
        """Generate message for module-level function error"""
        return (
            f"@{decorator_name} cannot be applied to module-level functions. "
            f"Access control decorators can only be used on class methods.\n"
            f"Did you mean to put this function inside a class?"
        )
    
    @staticmethod
    def _generate_inheritance_syntax_error(decorator_name: str, usage_type: str) -> str:
        """Generate message for inheritance syntax on methods"""
        return (
            f"@{decorator_name} cannot be applied to {usage_type} with inheritance syntax. "
            f"Inheritance decorators can only be applied to classes.\n"
            f"Did you mean: @{decorator_name} (without parentheses) for {usage_type} access control?"
        )
    
    @staticmethod
    def _generate_non_class_target_message(decorator_name: str) -> str:
        """Generate message for non-class target error"""
        return (
            f"@{decorator_name} with inheritance syntax can only be applied to classes.\n"
            f"Did you mean: @{decorator_name} (without parentheses) for method access control?"
        )
    
    @staticmethod
    def _generate_invalid_inheritance_message(decorator_name: str) -> str:
        """Generate message for invalid inheritance arguments"""
        return (
            f"@{decorator_name} inheritance decorator requires class arguments only.\n"
            f"Did you mean: @{decorator_name}(<ClassName>) where <ClassName> is a class?"
        )
    
    @staticmethod
    def _generate_duplicate_application_message(decorator_name: str, context: Dict[str, Any]) -> str:
        """Generate message for duplicate application error"""
        target_name = context.get('target_name', 'method')
        class_name = context.get('class_name', 'ClassName')
        func_obj = context.get('func_obj')
        
        # Extract enhanced method information
        if func_obj:
            method_type, arguments, wrapper_decorators = MethodInspector.extract_method_info(func_obj)
        else:
            method_type = context.get('method_type', 'method')
            arguments = context.get('arguments', 'self')
            wrapper_decorators = context.get('wrapper_decorators', [])
        
        # Build the corrected suggestion
        suggestion = MessageGenerator._build_method_suggestion(
            decorator_name, target_name, arguments, method_type, wrapper_decorators
        )
        
        # Format the target name appropriately
        formatted_target = TargetFormatter.format_qualified_target(class_name, target_name, method_type)
        
        return (
            f"@{decorator_name} was applied to {formatted_target} more than once!\n"
            f"Did you mean:\n"
            f"{suggestion}\n"
            f"?"
        )
    
    @staticmethod
    def _generate_fallback_message(decorator_name: str, usage_type: str) -> str:
        """Generate fallback error message"""
        return (
            f"@{decorator_name} decorator cannot be applied to {usage_type}. "
            f"Access control decorators can only be used on class methods."
        )
    
    @staticmethod
    def _build_corrected_suggestion(
        decorators: List[str],
        method_name: str,
        arguments: str,
        return_annotation: str,
        function_body: str,
        wrapper_decorators: List[str]
    ) -> str:
        """Build a corrected code suggestion"""
        if wrapper_decorators:
            decorator_lines = [f"@{dec}" for dec in wrapper_decorators] + [f"@{dec}" for dec in decorators]
        else:
            decorator_lines = [f"@{dec}" for dec in decorators]
        
        return (
            f"{chr(10).join(decorator_lines)}\n"
            f"def {method_name}({arguments}){return_annotation}:\n"
            f"{function_body}"
        )
    
    @staticmethod
    def _build_method_suggestion(
        decorator_name: str,
        target_name: str,
        arguments: str,
        method_type: str,
        wrapper_decorators: List[str]
    ) -> str:
        """Build method-specific suggestion"""
        if wrapper_decorators:
            decorator_lines = [f"@{dec}" for dec in wrapper_decorators] + [f"@{decorator_name}"]
        else:
            decorator_lines = [f"@{decorator_name}"]
        
        # Choose appropriate body based on method type
        if method_type == 'property':
            body = "    return value"
        else:
            body = "    pass"
        
        return (
            f"{chr(10).join(decorator_lines)}\n"
            f"def {target_name}({arguments}):\n"
            f"{body}"
        )
