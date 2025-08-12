#!/usr/bin/env python3
"""
Test cases for property setter access control and multiple decorator conflicts.
These tests cover the two important fixes:
1. Property setters are now properly access controlled
2. Multiple conflicting decorators are detected and prevented
"""

import pytest
import sys
import os

# Add the limen module to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from limen import private, protected, public
from limen.exceptions import PermissionDeniedError, DecoratorConflictError


class TestPropertySetterAccessControl:
    """Test that property setters are properly access controlled"""
    
    def test_private_property_setter_same_class(self):
        """Test that private property setters work within the same class"""
        
        class TestClass:
            def __init__(self):
                self._value = "initial"
            
            @private
            @property
            def secure_value(self):
                return self._value
            
            @secure_value.setter
            def secure_value(self, value):
                self._value = value
            
            def internal_get(self):
                return self.secure_value
            
            def internal_set(self, value):
                self.secure_value = value
        
        obj = TestClass()
        
        # Same-class access should work
        assert obj.internal_get() == "initial"
        obj.internal_set("new_value")
        assert obj.internal_get() == "new_value"
    
    def test_private_property_setter_external_access_blocked(self):
        """Test that private property setters block external access"""
        
        class TestClass:
            def __init__(self):
                self._value = "initial"
            
            @private
            @property
            def secure_value(self):
                return self._value
            
            @secure_value.setter
            def secure_value(self, value):
                self._value = value
        
        obj = TestClass()
        
        # External access should be blocked for both getter and setter
        with pytest.raises(PermissionDeniedError, match="Access denied to private property"):
            _ = obj.secure_value
            
        with pytest.raises(PermissionDeniedError, match="Access denied to private property"):
            obj.secure_value = "hacked"
    
    def test_protected_property_setter_inheritance(self):
        """Test that protected property setters work with inheritance"""
        
        class Base:
            def __init__(self):
                self._value = "base"
            
            @protected
            @property
            def family_value(self):
                return self._value
            
            @family_value.setter
            def family_value(self, value):
                self._value = value
        
        @protected(Base)
        class Derived(Base):
            def access_family_value(self):
                return self.family_value
            
            def set_family_value(self, value):
                self.family_value = value
        
        obj = Derived()
        
        # Inheritance access should work
        assert obj.access_family_value() == "base"
        obj.set_family_value("derived")
        assert obj.access_family_value() == "derived"
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError, match="Access denied to protected property"):
            _ = obj.family_value


class TestMultipleDecoratorConflicts:
    """Test that multiple conflicting decorators are detected and prevented"""
    
    def test_private_protected_conflict(self):
        """Test that @private @protected raises a conflict error"""
        
        with pytest.raises(DecoratorConflictError, match="Conflicting access level decorators on.*\\(\\):.*already has"):
            class TestClass:
                @private
                @protected
                def conflicted_method(self):
                    return 'data'
    
    def test_protected_public_conflict(self):
        """Test that @protected @public raises a conflict error"""
        
        with pytest.raises(DecoratorConflictError, match="Conflicting access level decorators on.*already has"):
            class TestClass:
                @protected
                @public
                def conflicted_method(self):
                    return 'data'
    
    def test_private_public_conflict(self):
        """Test that @private @public raises a conflict error"""
        
        with pytest.raises(DecoratorConflictError, match="Conflicting access level decorators on.*already has"):
            class TestClass:
                @private
                @public
                def conflicted_method(self):
                    return 'data'
    
    def test_same_decorator_twice_not_allowed(self):
        """Test that applying the same decorator twice raises an error"""
        
        # This should raise an error now due to duplicate decorator validation
        with pytest.raises(DecoratorConflictError, match="was applied to.*more than once"):
            class TestClass:
                @private
                @private
                def double_private(self):
                    return 'data'
    
    def test_multiple_conflicts_with_staticmethod(self):
        """Test that conflicts are detected even with @staticmethod"""
        
        with pytest.raises(DecoratorConflictError, match="Conflicting access level decorators on.*already has"):
            class TestClass:
                @private
                @protected
                @staticmethod
                def conflicted_static(self):
                    return 'data'
    
    def test_multiple_conflicts_with_property(self):
        """Test that conflicts are detected even with @property"""
        
        with pytest.raises(DecoratorConflictError, match="Conflicting access level decorators on.*already has"):
            class TestClass:
                @private
                @protected
                @property
                def conflicted_prop(self):
                    return 'data'
    
    def test_complex_decorator_order(self):
        """Test that decorator order doesn't matter for conflict detection"""
        
        # Test different orders
        with pytest.raises(DecoratorConflictError, match="Conflicting access level decorators on.*already has"):
            class TestClass1:
                @staticmethod
                @private
                @protected
                def method1(self):
                    return 'data'
        
        with pytest.raises(DecoratorConflictError, match="Conflicting access level decorators on.*already has"):
            class TestClass2:
                @property
                @protected
                @private
                def method2(self):
                    return 'data'
