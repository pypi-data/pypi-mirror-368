"""
Test edge cases and boundary conditions for access control
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from limen import private, protected, public
from limen.exceptions import PermissionDeniedError
from limen.system.access_control import get_access_control_system

@pytest.mark.edge_cases
@pytest.mark.cpp_semantics
class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_enforcement_toggle(self):
        """Test that enforcement can be toggled on/off"""
        class TestClass:
            @private
            def private_method(self):
                return "private_result"
        
        obj = TestClass()
        
        # With enforcement enabled (default), access should be blocked
        with pytest.raises(PermissionDeniedError):
            obj.private_method()
        
                # Disable enforcement - access should be allowed
        access_control = get_access_control_system()
        access_control.enforcement_enabled = False
        
        # Now access should work
        assert obj.private_method() == "private_result"
        
        # Re-enable enforcement
        access_control.enforcement_enabled = True
        
        # Access should be blocked again
        with pytest.raises(PermissionDeniedError):
            obj.private_method()
    
    def test_nested_class_access(self):
        """Test access control with nested classes"""
        class Outer:
            @private
            def outer_private(self):
                return "outer_private"
            
            class Nested:
                @private
                def nested_private(self):
                    return "nested_private"
                
                def try_access_outer(self, outer_obj):
                    try:
                        return outer_obj.outer_private()
                    except PermissionDeniedError:
                        return 'BLOCKED'
            
            def try_access_nested(self, nested_obj):
                try:
                    return nested_obj.nested_private()
                except PermissionDeniedError:
                    return 'BLOCKED'
        
        outer_obj = Outer()
        nested_obj = Outer.Nested()
        
        # Nested classes should not automatically have access to outer private members
        assert nested_obj.try_access_outer(outer_obj) == 'BLOCKED'
        
        # Outer classes should not automatically have access to nested private members
        assert outer_obj.try_access_nested(nested_obj) == 'BLOCKED'
    
    def test_method_override_access_control(self):
        """Test access control when methods are overridden"""
        class Base:
            @private
            def private_method(self):
                return "base_private"
            
            @protected
            def protected_method(self):
                return "base_protected"
        
        class Derived(Base):
            # Override with different access level
            def private_method(self):  # Now public
                return "derived_public"
            
            @private
            def protected_method(self):  # Now private
                return "derived_private"
            
            def test_access(self):
                return {
                    'private_method': self.private_method(),  # Should work - now public
                    'base_private': super().private_method() if hasattr(super(), 'private_method') else 'NO_ACCESS'
                }
        
        derived_obj = Derived()
        
        # Overridden public method should be accessible
        assert derived_obj.private_method() == "derived_public"
        
        # Overridden private method should not be accessible externally
        with pytest.raises(PermissionDeniedError):
            derived_obj.protected_method()
    
    def test_property_getter_access_control(self):
        """Test access control for property getters (setter control is limited due to Python property limitations)"""
        class TestClass:
            def __init__(self):
                self._value = "initial"
            
            @private
            @property
            def private_property(self):
                return self._value
            
            # Note: Property setters added with @property.setter don't inherit access control
            # This is a Python limitation - the setter is added after our decorator
            
            def internal_access(self):
                return self.private_property
            
            def internal_set_via_method(self, value):
                # Internal setting should use a private method instead
                self._set_private_value(value)
            
            @private
            def _set_private_value(self, value):
                self._value = value
        
        obj = TestClass()
        
        # Internal access should work
        assert obj.internal_access() == "initial"
        obj.internal_set_via_method("new_value")
        assert obj.internal_access() == "new_value"
        
        # External getter access should be blocked
        with pytest.raises(PermissionDeniedError):
            _ = obj.private_property
        
        # External setter access to the private method should be blocked
        with pytest.raises(PermissionDeniedError):
            obj._set_private_value("external_value")
    
    def test_multiple_inheritance_diamond_problem(self):
        """Test access control with diamond inheritance pattern"""
        class GrandParent:
            @protected
            def method(self):
                return "grandparent"
        
        class Parent1(GrandParent):
            pass
        
        class Parent2(GrandParent):
            @private
            def method(self):  # Override with private
                return "parent2_private"
        
        class Child(Parent1, Parent2):
            def test_access(self):
                # Which method gets called depends on MRO
                try:
                    return self.method()
                except PermissionDeniedError:
                    return 'BLOCKED'
        
        child_obj = Child()
        
        # The result depends on method resolution order
        # MRO: Child, Parent1, Parent2, GrandParent
        # Parent2's private method comes before GrandParent's protected method
        # So access should be blocked because Parent2's method is private
        result = child_obj.test_access()
        assert result == 'BLOCKED'  # Parent2's private method blocks access
    
    def test_descriptor_protocol_compatibility(self):
        """Test that access control works with custom descriptors"""
        class CustomDescriptor:
            def __init__(self, value):
                self.value = value
            
            def __get__(self, obj, objtype=None):
                if obj is None:
                    return self
                return self.value
            
            def __set__(self, obj, value):
                self.value = value
        
        class TestClass:
            custom_attr = CustomDescriptor("descriptor_value")
            
            @private
            @property 
            def private_descriptor_access(self):
                return self.custom_attr
        
        obj = TestClass()
        
        # Custom descriptor should work normally
        assert obj.custom_attr == "descriptor_value"
        
        # Private property accessing descriptor should follow access control
        with pytest.raises(PermissionDeniedError):
            _ = obj.private_descriptor_access
    
    def test_metaclass_interaction(self):
        """Test that access control works with metaclasses"""
        class AccessControlMeta(type):
            def __new__(mcs, name, bases, dct):
                # Metaclass that adds a method
                dct['meta_added_method'] = lambda self: "meta_method"
                return super().__new__(mcs, name, bases, dct)
        
        class TestClass(metaclass=AccessControlMeta):
            @private
            def private_method(self):
                return "private_method"
        
        obj = TestClass()
        
        # Metaclass-added method should work normally
        assert obj.meta_added_method() == "meta_method"
        
        # Private method should still be controlled
        with pytest.raises(PermissionDeniedError):
            obj.private_method()
    
    def test_class_method_with_inheritance_edge_case(self):
        """Test edge case where class method is called on derived class"""
        class Base:
            @private
            @classmethod
            def private_class_method(cls):
                return f"private_class_{cls.__name__}"
        
        class Derived(Base):
            @classmethod
            def try_call_private(cls):
                # This should fail even though we're calling on Derived
                return cls.private_class_method()
        
        # Direct call on derived should fail
        with pytest.raises(PermissionDeniedError):
            Derived.private_class_method()
        
        # Call through derived class method should also fail
        with pytest.raises(PermissionDeniedError):
            Derived.try_call_private()
    
    def test_static_method_inheritance_edge_case(self):
        """Test edge case where static method is inherited"""
        class Base:
            @private
            @staticmethod
            def private_static_method():
                return "private_static"
        
        class Derived(Base):
            @staticmethod
            def try_call_private():
                # This should fail - private static not accessible from derived
                return Base.private_static_method()
        
        # Direct call should fail
        with pytest.raises(PermissionDeniedError):
            Derived.private_static_method()
        
        # Call through derived static method should also fail
        with pytest.raises(PermissionDeniedError):
            Derived.try_call_private()
