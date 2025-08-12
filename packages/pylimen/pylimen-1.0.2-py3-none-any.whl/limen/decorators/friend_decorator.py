"""
Friend decorator implementation
"""
from typing import Type, Callable, Union
import inspect
from ..system import get_access_control_system


def friend(target_class: Type) -> Callable:
    """@friend decorator for establishing friend relationships with classes, functions, or methods"""
    def decorator(friend_entity: Union[Type, Callable]) -> Union[Type, Callable]:
        access_control = get_access_control_system()
        
        # Debug output
        print(f"Friend decorator applied to: {type(friend_entity)}")
        
        if inspect.isclass(friend_entity):
            # Friend class
            print("  -> Registering friend class")
            access_control.register_friend(target_class, friend_entity)
            access_control.emit_event('friendship_established', {
                'target_class': target_class.__name__,
                'friend_class': friend_entity.__name__
            })
        elif inspect.isfunction(friend_entity):
            # Check if this function will become a method (has 'self' or 'cls' parameter)
            print("  -> Function detected")
            sig = inspect.signature(friend_entity)
            params = list(sig.parameters.keys())
            
            if params and params[0] in ('self', 'cls'):
                # This is a method that will be bound to a class
                print("  -> Marking as friend method")
                friend_entity._limen_friend_target = target_class
                friend_entity._limen_is_friend_method = True
                
                # For methods with 'cls' parameter, we need to handle the case where
                # @classmethod might be applied after @friend. We'll mark the function
                # with a special attribute and let the metaclass handle it.
                if params and params[0] == 'cls':
                    friend_entity._limen_expect_classmethod = True
                    return friend_entity
                
                # Create a public descriptor to ensure __set_name__ is called
                # Mark it as created by friend decorator for conflict resolution
                from ..descriptors.factory import DescriptorFactory
                from ..core.enums import AccessLevel
                descriptor = DescriptorFactory.create_method_descriptor(friend_entity, AccessLevel.PUBLIC)
                descriptor._created_by_friend_decorator = True
                return descriptor
            else:
                # Standalone function
                print("  -> Registering friend function")
                access_control.register_friend_function(target_class, friend_entity)
                access_control.emit_event('friend_function_established', {
                    'target_class': target_class.__name__,
                    'friend_function': friend_entity.__name__
                })
        elif isinstance(friend_entity, (classmethod, staticmethod)):
            # Handle classmethod and staticmethod objects uniformly
            original_func = friend_entity.__func__
            if inspect.isfunction(original_func):
                original_func._limen_friend_target = target_class
                original_func._limen_is_friend_method = True
                # Create appropriate descriptor based on type
                from ..descriptors.factory import DescriptorFactory
                from ..core.enums import AccessLevel
                descriptor = DescriptorFactory.create_method_descriptor(friend_entity, AccessLevel.PUBLIC)
                descriptor._created_by_friend_decorator = True
                return descriptor
        elif hasattr(friend_entity, '_func_or_value') and hasattr(friend_entity, '_access_level'):
            # This is an access control descriptor (e.g., from @private)
            print("  -> Access control descriptor detected")
            original_func = friend_entity._func_or_value
            print(f"  -> Original function type: {type(original_func)}")
            print(f"  -> Is function: {inspect.isfunction(original_func)}")
            if inspect.isfunction(original_func):
                print(f"  -> Setting friend attributes on function {id(original_func)}")
                original_func._limen_friend_target = target_class
                original_func._limen_is_friend_method = True
                print(f"  -> Set _limen_friend_target to {target_class}")
                print("  -> Checking if attributes were set...")
                print(f"  -> Has _limen_friend_target: {hasattr(original_func, '_limen_friend_target')}")
                print(f"  -> Has _limen_is_friend_method: {hasattr(original_func, '_limen_is_friend_method')}")
            else:
                print(f"  -> WARNING: Original func is not a function, it's {type(original_func)}")
            # Don't emit event here, will be emitted when the descriptor's __set_name__ is called
        else:
            raise ValueError(f"@friend can only be applied to classes, functions, or access control descriptors, not {type(friend_entity)}")
        
        return friend_entity
    return decorator


def _register_friend_method_if_needed(method: Callable, owner_class: Type) -> None:
    """
    Register a method as a friend if it was decorated with @friend.
    This is called when a class is created and methods are bound.
    """
    if hasattr(method, '_limen_friend_target') and hasattr(method, '_limen_is_friend_method'):
        target_class = method._limen_friend_target
        access_control = get_access_control_system()
        access_control.register_friend_method(target_class, owner_class, method.__name__)
        access_control.emit_event('friend_method_established', {
            'target_class': target_class.__name__,
            'friend_class': owner_class.__name__,
            'method_name': method.__name__
        })
        # Clean up the temporary attributes
        delattr(method, '_limen_friend_target')
        delattr(method, '_limen_is_friend_method')
