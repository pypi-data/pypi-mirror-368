"""
Test C++ private access semantics
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from limen import private, protected, public
from limen.exceptions import PermissionDeniedError

@pytest.mark.cpp_semantics
@pytest.mark.access_control
class TestPrivateAccessSemantics:
    """Test that private access follows C++ semantics exactly"""
    
    def test_private_method_same_class_access(self, sample_classes):
        """Private methods should be accessible from same class"""
        Base = sample_classes['Base']
        obj = Base()
        
        # Internal access should work
        results = obj.call_private_methods()
        assert results['private_method'] == 'private_method_result'
        assert results['private_static'] == 'private_static_result'
        assert results['private_class'] == 'private_class_result_Base'
        assert results['private_prop'] == 'private_prop_result'
    
    def test_private_method_derived_class_blocked(self, sample_classes):
        """Private methods should NOT be accessible from derived classes (C++ semantics)"""
        Derived = sample_classes['Derived']
        obj = Derived()
        
        # Derived class should NOT have access to base private methods
        results = obj.try_access_base_private()
        assert results['private_method'] == 'BLOCKED'
        assert results['private_static'] == 'BLOCKED'
        assert results['private_class'] == 'BLOCKED'
        assert results['private_prop'] == 'BLOCKED'
    
    def test_private_method_external_access_blocked(self, sample_classes):
        """Private methods should NOT be accessible from external code"""
        Base = sample_classes['Base']
        Unrelated = sample_classes['Unrelated']
        
        base_obj = Base()
        unrelated_obj = Unrelated()
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError, match="Access denied to private method"):
            base_obj.private_method()
    
    def test_private_static_method_inheritance_blocked(self, sample_classes):
        """Private static methods should not be accessible from derived classes"""
        Base = sample_classes['Base']
        Derived = sample_classes['Derived']
        
        # Direct call from derived class should fail
        with pytest.raises(PermissionDeniedError):
            Derived.private_static()
    
    def test_private_class_method_inheritance_blocked(self, sample_classes):
        """Private class methods should not be accessible from derived classes"""  
        Base = sample_classes['Base']
        Derived = sample_classes['Derived']
        
        # Direct call from derived class should fail
        with pytest.raises(PermissionDeniedError):
            Derived.private_class()
    
    def test_private_property_inheritance_blocked(self, sample_classes):
        """Private properties should not be accessible from derived classes"""
        Derived = sample_classes['Derived']
        derived_obj = Derived()
        
        # Direct access from derived instance should fail
        with pytest.raises(PermissionDeniedError):
            _ = derived_obj.private_prop


@pytest.mark.cpp_semantics
@pytest.mark.access_control
class TestProtectedAccessSemantics:
    """Test that protected access follows C++ semantics"""
    
    def test_protected_method_same_class_access(self, sample_classes):
        """Protected methods should be accessible from same class"""
        Base = sample_classes['Base']
        obj = Base()
        
        # Same class access should work (called from within the class)
        assert obj.call_protected_method() == "protected_method_result"
    
    def test_protected_method_inheritance_access(self, sample_classes):
        """Protected methods should be accessible from derived classes"""
        Derived = sample_classes['Derived']
        obj = Derived()
        
        # Derived class should have access
        results = obj.try_access_base_protected()
        assert results['protected_method'] == 'protected_method_result'
        assert results['protected_static'] == 'protected_static_result'
        # When called from derived class, class method should show derived class name
        assert results['protected_class'] == 'protected_class_result_Derived'
    
    def test_protected_method_external_access_blocked(self, sample_classes):
        """Protected methods should NOT be accessible from external code"""
        Base = sample_classes['Base']
        
        base_obj = Base()
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError, match="Access denied to protected method"):
            base_obj.protected_method()
    
    def test_protected_unrelated_class_blocked(self, sample_classes):
        """Protected methods should NOT be accessible from unrelated classes"""
        Base = sample_classes['Base']
        Unrelated = sample_classes['Unrelated']
        
        base_obj = Base()
        unrelated_obj = Unrelated()
        
        # Unrelated class should not be able to access protected methods
        with pytest.raises(PermissionDeniedError, match="Access denied to protected method"):
            base_obj.protected_method()


@pytest.mark.cpp_semantics
@pytest.mark.access_control  
class TestPublicAccessSemantics:
    """Test that public access is unrestricted"""
    
    def test_public_method_universal_access(self, sample_classes):
        """Public methods should be accessible from anywhere"""
        Base = sample_classes['Base']
        Derived = sample_classes['Derived']
        Unrelated = sample_classes['Unrelated']
        
        base_obj = Base()
        derived_obj = Derived()
        unrelated_obj = Unrelated()
        
        # All access should work
        assert base_obj.public_method() == "public_method_result"
        assert derived_obj.public_method() == "public_method_result"
        
        # Unrelated class should also be able to access
        assert unrelated_obj.access_other_public(base_obj) == "public_method_result"
