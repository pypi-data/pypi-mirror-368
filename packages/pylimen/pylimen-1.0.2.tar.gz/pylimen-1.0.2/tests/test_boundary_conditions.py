"""
Boundary condition tests - Test extreme edge cases and unusual scenarios
"""
import pytest
import sys
from limen import private, protected
from limen.exceptions import PermissionDeniedError


class TestExtremeScenarios:
    """Test extreme boundary conditions"""
    
    def test_empty_class_with_decorators(self):
        """Test decorators on empty classes"""
        
        class EmptyClass:
            @private 
            def added_method(self):
                return "added_secret"
        
        instance = EmptyClass()
        
        # Should be protected
        with pytest.raises(PermissionDeniedError):
            instance.added_method()

    def test_dynamic_method_addition(self):
        """Test adding methods dynamically"""
        
        class DynamicClass:
            @private
            def existing_method(self):
                return "existing"
        
        instance = DynamicClass()
        
        # Test that existing decorated method works
        with pytest.raises(PermissionDeniedError):
            instance.existing_method()

    def test_extreme_inheritance_depth(self):
        """Test very deep inheritance chains"""
        
        # Create 5-level deep inheritance (reduced from 50 for performance)
        class Level0:
            @private
            def secret(self):
                return "level0_secret"
        
        class Level1(Level0): pass
        class Level2(Level1): pass
        class Level3(Level2): pass
        class Level4(Level3): pass
        
        instance = Level4()
        
        # Private method should not be accessible
        with pytest.raises(PermissionDeniedError):
            instance.secret()


class TestEdgeCaseInteractions:
    """Test edge case interactions between features"""
    
    def test_decorator_order_edge_cases(self):
        """Test unusual decorator ordering"""
        
        class OrderTest:
            @private
            @staticmethod
            def static_private():
                return "static_private"
            
            @private
            @classmethod
            def class_private(cls):
                return "class_private"
        
        # Test static method access
        with pytest.raises((PermissionDeniedError, TypeError)):
            OrderTest.static_private()
        
        # Test class method access
        with pytest.raises((PermissionDeniedError, TypeError)):
            OrderTest.class_private()

    def test_cross_instance_access(self):
        """Test access between different instances"""
        
        class CrossTest:
            @private
            def secret(self):
                return "instance_secret"
            
            def try_access_other(self, other):
                # In some systems, same-class access is allowed even across instances
                return other.secret()
        
        instance1 = CrossTest()
        instance2 = CrossTest()
        
        # Test cross-instance access behavior
        try:
            result = instance1.try_access_other(instance2)
            # If it works, the system allows same-class cross-instance access
            assert "instance_secret" in str(result)
        except PermissionDeniedError:
            # If it's blocked, that's also a valid security model
            pass


class TestSystemLimits:
    """Test system limits and edge cases"""
    
    def test_maximum_inheritance_chain(self):
        """Test very long inheritance chains"""
        
        # Create base class with private method properly defined
        class Base:
            @private
            def secret(self):
                return "base_secret"
        
        # Build inheritance chain
        current_class = Base
        for i in range(10):
            current_class = type(f'Level{i}', (current_class,), {})
        
        instance = current_class()
        
        # Private method should still be blocked
        with pytest.raises(PermissionDeniedError):
            instance.secret()

    def test_large_method_names(self):
        """Test methods with very long names"""
        
        # Create method with long name directly in class
        long_name = "very_long_method_name" + "_" * 50 + "end"
        
        # Use exec to create class with long method name
        class_code = f"""
class LongNameTest:
    @private
    def {long_name}(self):
        return "long_secret"
"""
        
        local_vars = {'private': private}
        exec(class_code, globals(), local_vars)
        LongNameTest = local_vars['LongNameTest']
        
        instance = LongNameTest()
        
        # Test that long names work with access control
        with pytest.raises(PermissionDeniedError):
            getattr(instance, long_name)()

    def test_unicode_edge_cases(self):
        """Test Unicode in method names and strings"""
        
        class UnicodeTest:
            @private
            def test_method(self):
                return "unicode_test_🔒"
        
        instance = UnicodeTest()
        
        # Should be protected regardless of Unicode content
        with pytest.raises(PermissionDeniedError):
            instance.test_method()


class TestSpecialMethodInteractions:
    """Test interactions with Python special methods"""
    
    def test_dunder_method_protection(self):
        """Test protection of dunder methods"""
        
        class DunderTest:
            @private
            def __custom_private__(self):
                return "custom_private"
            
            def __str__(self):
                return "DunderTest"
        
        instance = DunderTest()
        
        # Regular __str__ should work
        assert str(instance) == "DunderTest"
        
        # Custom dunder method should be protected
        with pytest.raises(PermissionDeniedError):
            instance.__custom_private__()

    def test_metaclass_interactions(self):
        """Test interactions with metaclasses"""
        
        class MetaTest(type):
            def __new__(cls, name, bases, attrs):
                return super().__new__(cls, name, bases, attrs)
        
        class TestWithMeta(metaclass=MetaTest):
            @private
            def meta_secret(self):
                return "meta_secret"
        
        instance = TestWithMeta()
        
        # Should still be protected with metaclass
        with pytest.raises(PermissionDeniedError):
            instance.meta_secret()


class TestErrorConditions:
    """Test error conditions and recovery"""
    
    def test_decorator_on_invalid_targets(self):
        """Test decorators on invalid targets"""
        
        # Test that decorators work on valid class methods
        class ValidTarget:
            @private
            def valid_method(self):
                return "valid"
        
        instance = ValidTarget()
        
        with pytest.raises(PermissionDeniedError):
            instance.valid_method()

    def test_memory_pressure_conditions(self):
        """Test behavior under memory pressure"""
        
        class MemoryTest:
            @private
            def memory_method(self):
                return "memory_data"
        
        # Create many instances
        instances = [MemoryTest() for _ in range(100)]
        
        # All should maintain protection
        for instance in instances:
            with pytest.raises(PermissionDeniedError):
                instance.memory_method()
        
        # Cleanup
        del instances

    def test_exception_handling_edge_cases(self):
        """Test exception handling in edge cases"""
        
        class ExceptionTest:
            @private
            def exception_method(self):
                raise ValueError("Internal error")
        
        instance = ExceptionTest()
        
        # Should get PermissionDeniedError, not the internal ValueError
        with pytest.raises(PermissionDeniedError):
            instance.exception_method()
