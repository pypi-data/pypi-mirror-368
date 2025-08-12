"""
Test compositional decorator functionality (@private @staticmethod etc.)
"""
import pytest

from limen import private, protected, public, friend
from limen.exceptions import PermissionDeniedError

@pytest.mark.composition
@pytest.mark.cpp_semantics
class TestCompositionalDecorators:
    """Test that compositional decorators work correctly with C++ semantics"""
    
    def test_private_staticmethod_composition(self):
        """Test @private @staticmethod composition"""
        class TestClass:
            @private
            @staticmethod
            def private_static_method():
                return "private_static_result"
            
            def internal_caller(self):
                return self.private_static_method()
        
        class Derived(TestClass):
            def try_call_private_static(self):
                return self.private_static_method()
        
        # Same class access should work
        obj = TestClass()
        assert obj.internal_caller() == "private_static_result"
        
        # Derived class access should be blocked
        derived_obj = Derived()
        with pytest.raises(PermissionDeniedError):
            derived_obj.try_call_private_static()
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError):
            TestClass.private_static_method()
    
    def test_protected_staticmethod_composition(self):
        """Test @protected @staticmethod composition"""
        class TestClass:
            @protected
            @staticmethod
            def protected_static_method():
                return "protected_static_result"
            
            def internal_caller(self):
                return self.protected_static_method()
        
        class Derived(TestClass):
            def call_protected_static(self):
                return self.protected_static_method()
        
        # Same class access should work
        obj = TestClass()
        assert obj.internal_caller() == "protected_static_result"
        
        # Derived class access should work
        derived_obj = Derived()
        assert derived_obj.call_protected_static() == "protected_static_result"
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError):
            TestClass.protected_static_method()
    
    def test_private_classmethod_composition(self):
        """Test @private @classmethod composition"""
        class TestClass:
            @private
            @classmethod
            def private_class_method(cls):
                return f"private_class_result_{cls.__name__}"
            
            @classmethod
            def internal_caller(cls):
                return cls.private_class_method()
        
        class Derived(TestClass):
            @classmethod
            def try_call_private_class(cls):
                return cls.private_class_method()
        
        # Same class access should work
        assert TestClass.internal_caller() == "private_class_result_TestClass"
        
        # Derived class access should be blocked (C++ semantics)
        with pytest.raises(PermissionDeniedError):
            Derived.try_call_private_class()
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError):
            TestClass.private_class_method()
    
    def test_protected_classmethod_composition(self):
        """Test @protected @classmethod composition"""
        class TestClass:
            @protected
            @classmethod
            def protected_class_method(cls):
                return f"protected_class_result_{cls.__name__}"
            
            @classmethod
            def internal_caller(cls):
                return cls.protected_class_method()
        
        class Derived(TestClass):
            @classmethod
            def call_protected_class(cls):
                return cls.protected_class_method()
        
        # Same class access should work
        assert TestClass.internal_caller() == "protected_class_result_TestClass"
        
        # Derived class access should work (C++ semantics)
        assert Derived.call_protected_class() == "protected_class_result_Derived"
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError):
            TestClass.protected_class_method()
    
    def test_private_property_composition(self):
        """Test @private @property composition"""
        class TestClass:
            @private
            @property
            def private_property(self):
                return "private_property_result"
            
            def internal_caller(self):
                return self.private_property
        
        class Derived(TestClass):
            def try_access_private_property(self):
                return self.private_property
        
        # Same class access should work
        obj = TestClass()
        assert obj.internal_caller() == "private_property_result"
        
        # Derived class access should be blocked
        derived_obj = Derived()
        with pytest.raises(PermissionDeniedError):
            derived_obj.try_access_private_property()
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError):
            _ = obj.private_property
    
    def test_protected_property_composition(self):
        """Test @protected @property composition"""
        class TestClass:
            @protected
            @property
            def protected_property(self):
                return "protected_property_result"
            
            def internal_caller(self):
                return self.protected_property
        
        class Derived(TestClass):
            def access_protected_property(self):
                return self.protected_property
        
        # Same class access should work
        obj = TestClass()
        assert obj.internal_caller() == "protected_property_result"
        
        # Derived class access should work
        derived_obj = Derived()
        assert derived_obj.access_protected_property() == "protected_property_result"
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError):
            _ = obj.protected_property
    
    def test_multiple_decorators_preferred_order(self):
        """Test that the preferred decorator order @private @staticmethod works correctly"""
        class TestClass1:
            @private
            @staticmethod
            def method1():
                return "result1"
        
        class TestClass2:
            @private
            @classmethod
            def method2(cls):
                return "result2"
        
        # Both should be blocked for external access
        with pytest.raises(PermissionDeniedError):
            TestClass1.method1()
        
        with pytest.raises(PermissionDeniedError):
            TestClass2.method2()
        
        # Note: While @staticmethod @private may work, @private @staticmethod is the preferred order
    
    def test_composition_with_regular_methods(self):
        """Test that composition works with regular instance methods"""
        class TestClass:
            @private
            def private_instance_method(self):
                return "private_instance_result"
            
            @protected
            def protected_instance_method(self):
                return "protected_instance_result"
            
            def internal_caller(self):
                return {
                    'private': self.private_instance_method(),
                    'protected': self.protected_instance_method()
                }
        
        class Derived(TestClass):
            def try_access_methods(self):
                results = {}
                try:
                    results['private'] = self.private_instance_method()
                except PermissionDeniedError:
                    results['private'] = 'BLOCKED'
                
                try:
                    results['protected'] = self.protected_instance_method()
                except PermissionDeniedError:
                    results['protected'] = 'BLOCKED'
                
                return results
        
        # Same class access should work
        obj = TestClass()
        results = obj.internal_caller()
        assert results['private'] == 'private_instance_result'
        assert results['protected'] == 'protected_instance_result'
        
        # Derived class access
        derived_obj = Derived()
        derived_results = derived_obj.try_access_methods()
        assert derived_results['private'] == 'BLOCKED'  # Private blocked from derived
        assert derived_results['protected'] == 'protected_instance_result'  # Protected accessible from derived
