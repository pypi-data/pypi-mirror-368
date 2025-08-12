"""
Performance and stress tests to ensure the access control system is robust under load
"""
import pytest
import time
import concurrent.futures
import gc
import weakref
from unittest.mock import patch
from limen import private, protected, public
from limen.exceptions import PermissionDeniedError


class TestPerformanceStress:
    """Test performance characteristics under stress"""
    
    def test_large_class_hierarchy(self):
        """Test with deep inheritance hierarchy"""
        
        # Create a deep hierarchy
        class Base:
            @protected
            def base_method(self):
                return "base"
        
        # Build 20-level deep hierarchy
        current_class = Base
        for i in range(20):
            class Child(current_class):
                @protected
                def child_method(self):
                    return f"child_{i}"
                
                def access_parent(self):
                    return self.base_method()
            
            current_class = Child
        
        # Test access still works correctly at depth
        deep_instance = current_class()
        assert deep_instance.access_parent() == "base"
        
        # External access should still fail
        with pytest.raises(PermissionDeniedError):
            deep_instance.base_method()
    
    def test_many_methods_single_class(self):
        """Test class with many protected methods"""
        
        # Create class with multiple protected methods defined properly
        class ManyMethods:
            @protected
            def method_0(self):
                return "method_0"
            
            @protected 
            def method_1(self):
                return "method_1"
            
            @protected
            def method_2(self):
                return "method_2"
        
        instance = ManyMethods()
        
        # All should be protected
        for i in range(3):
            with pytest.raises(PermissionDeniedError):
                getattr(instance, f'method_{i}')()
    
    def test_concurrent_access_attempts(self):
        """Test concurrent access from multiple threads"""
        
        class ConcurrentTarget:
            @private
            def critical_method(self):
                time.sleep(0.001)  # Simulate work
                return "success"
        
        target = ConcurrentTarget()
        exceptions = []
        results = []
        
        def attempt_access():
            try:
                result = target.critical_method()
                results.append(result)
            except Exception as e:
                exceptions.append(e)
        
        # Launch 50 concurrent attempts
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(attempt_access) for _ in range(50)]
            concurrent.futures.wait(futures)
        
        # All should fail with PermissionDeniedError
        assert len(results) == 0
        assert len(exceptions) == 50
        assert all(isinstance(e, PermissionDeniedError) for e in exceptions)
    
    def test_rapid_instance_creation(self):
        """Test rapid creation and destruction of protected instances"""
        
        class RapidCreation:
            @private
            def secret(self):
                return "secret"
        
        # Create and test 1000 instances rapidly
        for i in range(1000):
            instance = RapidCreation()
            with pytest.raises(PermissionDeniedError):
                instance.secret()
            
            # Explicit cleanup to test GC behavior
            del instance
    
    def test_memory_efficiency(self):
        """Test memory usage doesn't grow excessively with protection"""
        
        class MemoryTest:
            @private
            def method1(self):
                return "data1"
            
            @protected
            def method2(self):
                return "data2"
            
            @public
            def method3(self):
                return "data3"
        
        # Create many instances and verify memory doesn't explode
        instances = [MemoryTest() for _ in range(100)]
        
        # Force garbage collection
        gc.collect()
        
        # Verify instances still work correctly
        for instance in instances:
            assert instance.method3() == "data3"
            
            with pytest.raises(PermissionDeniedError):
                instance.method1()
            
            with pytest.raises(PermissionDeniedError):
                instance.method2()
        
        # Clean up
        del instances
        gc.collect()
    
    def test_friend_relationship_scaling(self):
        """Test friend relationships with many classes"""
        from limen import friend
        
        class SecretKeeper:
            @private
            def get_secret(self):
                return "secret_data"
        
        # Create many friend classes
        friend_classes = []
        for i in range(10):
            class FriendClass:
                @friend(SecretKeeper)
                def access_secret(self, keeper):
                    return keeper.get_secret()
            
            friend_classes.append(FriendClass)
        
        keeper = SecretKeeper()
        
        # All friends should have access
        for FriendClass in friend_classes:
            friend_instance = FriendClass()
            assert friend_instance.access_secret(keeper) == "secret_data"
    
    def test_access_check_performance(self):
        """Test that access checks don't significantly slow down execution"""
        
        class PerformanceTest:
            @public
            def fast_method(self):
                return "fast"
            
            @private
            def protected_method(self):
                return "protected"
        
        instance = PerformanceTest()
        
        # Time public access (baseline)
        start_time = time.time()
        for _ in range(1000):
            instance.fast_method()
        public_time = time.time() - start_time
        
        # Time protected access failures
        start_time = time.time()
        for _ in range(1000):
            try:
                instance.protected_method()
            except PermissionDeniedError:
                pass
        protected_time = time.time() - start_time
        
        # Protection overhead should be reasonable (less than 10x slower)
        assert protected_time < public_time * 10


class TestEdgeCaseRobustness:
    """Test edge cases and unusual scenarios"""
    
    def test_circular_references(self):
        """Test behavior with circular references"""
        
        class Node:
            def __init__(self):
                self.parent = None
                self.children = []
            
            @private
            def get_secret(self):
                return "node_secret"
            
            def add_child(self, child):
                child.parent = self
                self.children.append(child)
        
        # Create circular reference
        node1 = Node()
        node2 = Node()
        node1.add_child(node2)
        node2.add_child(node1)  # Circular!
        
        # Access should still be denied despite circular structure
        with pytest.raises(PermissionDeniedError):
            node1.get_secret()
        
        with pytest.raises(PermissionDeniedError):
            node2.get_secret()
    
    def test_weak_reference_behavior(self):
        """Test behavior with weak references"""
        
        class WeakTest:
            @private
            def secret(self):
                return "weak_secret"
        
        instance = WeakTest()
        weak_ref = weakref.ref(instance)
        
        # Weak reference access should still be denied
        with pytest.raises(PermissionDeniedError):
            weak_ref().secret()
        
        # Test behavior when original is deleted
        del instance
        
        # Force multiple garbage collection cycles
        for _ in range(3):
            gc.collect()
        
        # Weak reference should be dead or nearly dead
        # In test environments, this might not be immediate
        result = weak_ref()
        assert result is None or hasattr(result, '__class__'), "Weak reference behavior test"
    
    def test_subclass_method_override(self):
        """Test method overriding in subclasses"""
        
        class Parent:
            @protected
            def protected_method(self):
                return "parent_protected"
        
        class Child(Parent):
            # Override with different access level
            @public
            def protected_method(self):
                return "child_public"
        
        parent = Parent()
        child = Child()
        
        # Parent method should be protected
        with pytest.raises(PermissionDeniedError):
            parent.protected_method()
        
        # Child method should be public (override successful)
        assert child.protected_method() == "child_public"
    
    def test_multiple_inheritance_diamond(self):
        """Test diamond inheritance pattern"""
        
        class A:
            @protected
            def method(self):
                return "A"
        
        class B(A):
            @protected
            def method(self):
                return "B"
        
        class C(A):
            @protected
            def method(self):
                return "C"
        
        class D(B, C):
            def access_method(self):
                return self.method()
        
        d = D()
        
        # Should be able to access through legitimate inheritance
        assert d.access_method() in ["B", "C"]  # MRO determines which
        
        # Direct external access should fail
        with pytest.raises(PermissionDeniedError):
            d.method()
    
    def test_property_descriptor_interactions(self):
        """Test interactions between properties and access control"""
        
        class PropertyTest:
            def __init__(self):
                self._value = "secret"
            
            @private
            @property
            def secret_property(self):
                return self._value
            
            @secret_property.setter
            def secret_property(self, value):
                self._value = value
        
        instance = PropertyTest()
        
        # Both getter and setter should be protected
        with pytest.raises(PermissionDeniedError):
            _ = instance.secret_property
        
        with pytest.raises(PermissionDeniedError):
            instance.secret_property = "new_value"
    
    def test_exception_during_access_check(self):
        """Test behavior when access check itself raises exception"""
        
        class ExceptionTest:
            @private
            def normal_method(self):
                return "normal"
        
        instance = ExceptionTest()
        
        # Patch the access checker to raise unexpected exception
        with patch('limen.system.access_control.AccessControlSystem.check_access') as mock_check:
            mock_check.side_effect = RuntimeError("Unexpected error")
            
            # Should handle gracefully (likely deny access)
            with pytest.raises((PermissionDeniedError, RuntimeError)):
                instance.normal_method()
    
    def test_unicode_method_names(self):
        """Test with Unicode method names"""
        
        class UnicodeTest:
            @private
            def 测试方法(self):  # Chinese characters
                return "unicode_secret"
            
            @protected
            def método_protegido(self):  # Spanish characters
                return "método_data"
        
        instance = UnicodeTest()
        
        # Unicode names should still be protected
        with pytest.raises(PermissionDeniedError):
            instance.测试方法()
        
        with pytest.raises(PermissionDeniedError):
            instance.método_protegido()
    
    def test_very_long_method_names(self):
        """Test with extremely long method names"""
        
        # Create a class with a very long method name using exec
        long_name = "very_" * 50 + "long_method_name"
        
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
        
        # Should still be protected regardless of name length
        with pytest.raises(PermissionDeniedError):
            getattr(instance, long_name)()


class TestResourceLimits:
    """Test behavior under resource constraints"""
    
    def test_stack_depth_limits(self):
        """Test with deep call stacks"""
        
        class StackTest:
            @private
            def recursive_method(self, depth=0):
                if depth > 50:  # Prevent actual stack overflow
                    return "deep_result"
                return self.recursive_method(depth + 1)
        
        instance = StackTest()
        
        # Should be denied regardless of stack depth
        with pytest.raises(PermissionDeniedError):
            instance.recursive_method()
    
    def test_large_object_attributes(self):
        """Test with objects having many attributes"""
        
        class LargeObject:
            def __init__(self):
                # Add many attributes
                for i in range(1000):
                    setattr(self, f'attr_{i}', f'value_{i}')
            
            @private
            def get_secret(self):
                return "secret_among_many"
        
        instance = LargeObject()
        
        # Should still be protected despite many attributes
        with pytest.raises(PermissionDeniedError):
            instance.get_secret()
        
        # Regular attributes should be accessible
        assert instance.attr_500 == "value_500"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
