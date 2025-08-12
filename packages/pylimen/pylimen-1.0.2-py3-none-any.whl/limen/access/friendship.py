"""
Manages friend relationships between classes and functions
"""
from typing import Type, Dict, Set, Callable


class FriendshipManager:
    """Manages friend relationships between classes and functions"""
    
    def __init__(self):
        self._relationships: Dict[str, Set[str]] = {}
        self._friend_functions: Dict[str, Set[str]] = {}  # target_class -> set of friend function names
        self._friend_methods: Dict[str, Dict[str, Set[str]]] = {}  # target_class -> {friend_class -> set of method names}
    
    def _get_class_name(self, cls: Type) -> str:
        """Safely get class name"""
        return cls.__name__ if cls else None
    
    def _ensure_target_exists(self, target_name: str, collection: Dict) -> None:
        """Ensure target exists in collection"""
        if target_name not in collection:
            collection[target_name] = set() if isinstance(list(collection.values())[0] if collection else set(), set) else {}
    
    def register_friend(self, target_class: Type, friend_class: Type) -> None:
        """Register a friend class relationship"""
        target_name = self._get_class_name(target_class)
        friend_name = self._get_class_name(friend_class)
        
        if not target_name or not friend_name:
            return
        
        if target_name not in self._relationships:
            self._relationships[target_name] = set()
        
        self._relationships[target_name].add(friend_name)
    
    def register_friend_function(self, target_class: Type, friend_function: Callable) -> None:
        """Register a friend function relationship"""
        target_name = self._get_class_name(target_class)
        
        if not target_name or not friend_function:
            return
            
        function_name = friend_function.__name__
        
        if target_name not in self._friend_functions:
            self._friend_functions[target_name] = set()
        
        self._friend_functions[target_name].add(function_name)
    
    def register_friend_method(self, target_class: Type, friend_class: Type, method_name: str) -> None:
        """Register a friend method relationship"""
        target_name = self._get_class_name(target_class)
        friend_name = self._get_class_name(friend_class)
        
        if not target_name or not friend_name or not method_name:
            return
        
        if target_name not in self._friend_methods:
            self._friend_methods[target_name] = {}
        
        if friend_name not in self._friend_methods[target_name]:
            self._friend_methods[target_name][friend_name] = set()
        
        self._friend_methods[target_name][friend_name].add(method_name)
    
    def is_friend(self, target_class: Type, caller_class: Type) -> bool:
        """Check if caller class is a friend of target"""
        target_name = self._get_class_name(target_class)
        caller_name = self._get_class_name(caller_class)
        
        if not target_name or not caller_name:
            return False
        
        return (target_name in self._relationships and 
                caller_name in self._relationships[target_name])
    
    def is_friend_function(self, target_class: Type, function_name: str) -> bool:
        """Check if function is a friend of target class"""
        target_name = self._get_class_name(target_class)
        
        if not target_name or not function_name:
            return False
        
        return (target_name in self._friend_functions and 
                function_name in self._friend_functions[target_name])
    
    def is_friend_method(self, target_class: Type, caller_class: Type, method_name: str) -> bool:
        """Check if a specific method of caller class is a friend of target class"""
        target_name = self._get_class_name(target_class)
        caller_name = self._get_class_name(caller_class)
        
        if not target_name or not caller_name or not method_name:
            return False
        
        return (target_name in self._friend_methods and 
                caller_name in self._friend_methods[target_name] and
                method_name in self._friend_methods[target_name][caller_name])
    
    def is_staticmethod_friend(self, target_class: Type, method_name: str) -> bool:
        """Check if a method (by name) is a friend method of target class (for staticmethods)"""
        target_name = self._get_class_name(target_class)
        
        if not target_name or not method_name:
            return False
        
        # Check all friend classes for this target to see if any have a method with this name
        if target_name in self._friend_methods:
            for caller_name, methods in self._friend_methods[target_name].items():
                if method_name in methods:
                    return True
        
        return False
    
    def get_friends_count(self) -> int:
        """Get total number of friend relationships (classes + functions + methods)"""
        class_friends = sum(len(friends) for friends in self._relationships.values())
        function_friends = sum(len(functions) for functions in self._friend_functions.values())
        method_friends = sum(
            len(methods) 
            for class_methods in self._friend_methods.values() 
            for methods in class_methods.values()
        )
        return class_friends + function_friends + method_friends
    
    def get_relationships_count(self) -> int:
        """Get number of classes with friends"""
        return len(self._relationships) + len(self._friend_functions) + len(self._friend_methods)
    
    def clear(self) -> None:
        """Clear all friend relationships"""
        self._relationships.clear()
        self._friend_functions.clear()
        self._friend_methods.clear()
