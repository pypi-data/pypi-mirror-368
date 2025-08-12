"""
Test C++ inheritance semantics (private, protected, public inheritance)
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from limen import private, protected, public
from limen.exceptions import PermissionDeniedError
from limen.core import InheritanceType

@pytest.mark.inheritance
@pytest.mark.cpp_semantics
class TestCppInheritanceSemantics:
    """Test C++ style inheritance with access control"""
    
    def test_public_inheritance_default(self):
        """Test that default Python inheritance is treated as public inheritance"""
        class Base:
            @protected
            def protected_method(self):
                return "base_protected"
            
            def public_method(self):
                return "base_public"
        
        class Derived(Base):
            def test_access(self):
                return {
                    'protected': self.protected_method(),  # Should work - protected accessible in derived
                    'public': self.public_method()  # Should work - public accessible everywhere
                }
        
        derived_obj = Derived()
        results = derived_obj.test_access()
        assert results['protected'] == 'base_protected'
        assert results['public'] == 'base_public'
        
        # External access to public should work
        assert derived_obj.public_method() == 'base_public'
        
        # External access to protected should be blocked
        with pytest.raises(PermissionDeniedError):
            derived_obj.protected_method()
    
    def test_private_inheritance_semantics(self):
        """Test that private inheritance blocks external access to base class methods"""
        from limen.utils.implicit import apply_implicit_access_control
        class Base:
            def public_method(self):
                return "base_public"
            
            def _protected_method(self):
                return "base_protected"
        # Apply implicit access control to base class
        apply_implicit_access_control(Base)
        # Create classes using decorators
        @private(Base)
        class PrivateDerived(Base):
            def child_method(self):
                return "child"
            
            def test_internal_access(self):
                # Within the class, should still be able to access base methods
                return {
                    'public': self.public_method(),
                    'protected': self._protected_method()
                }
        # Test that derived object can access base methods internally
        obj = PrivateDerived()
        results = obj.test_internal_access()
        assert results['public'] == 'base_public'
        assert results['protected'] == 'base_protected'
        # External access to base class methods should be blocked in private inheritance
        with pytest.raises(PermissionDeniedError):
            obj.public_method()
        with pytest.raises(PermissionDeniedError):
            obj._protected_method()
    
    def test_protected_inheritance_semantics(self):
        """Test protected inheritance - public members become protected"""
        class Base:
            def public_method(self):
                return "base_public"
            
            @protected
            def protected_method(self):
                return "base_protected"
        
        @protected(Base)
        class Derived(Base):
            def test_internal_access(self):
                return {
                    'public': self.public_method(),  # Now protected in derived
                    'protected': self.protected_method()  # Still protected
                }
        
        class FurtherDerived(Derived):
            def test_inherited_access(self):
                # FurtherDerived should be able to access both methods
                # since they're both protected in Derived
                return {
                    'public': self.public_method(),
                    'protected': self.protected_method()
                }
        
        derived_obj = Derived()
        further_obj = FurtherDerived()
        
        # Internal access within derived class should work
        results = derived_obj.test_internal_access()
        assert results['public'] == 'base_public'
        assert results['protected'] == 'base_protected'
        
        # Access from further derived class should work
        further_results = further_obj.test_inherited_access()
        assert further_results['public'] == 'base_public'
        assert further_results['protected'] == 'base_protected'
        
        # External access should be blocked for all members
        # because public became protected through protected inheritance
        with pytest.raises(PermissionDeniedError):
            derived_obj.public_method()  # Was public in base, now protected in derived
        
        with pytest.raises(PermissionDeniedError):
            derived_obj.protected_method()  # Still protected
    
    def test_multiple_inheritance_with_access_control(self):
        """Test multiple inheritance with different access levels"""
        class Base1:
            def base1_public(self):
                return "base1_public"
            
            @protected
            def base1_protected(self):
                return "base1_protected"
        
        class Base2:
            def base2_public(self):
                return "base2_public"
            
            @protected
            def base2_protected(self):
                return "base2_protected"
        
        @private(Base1)
        @protected(Base2)
        class MultiDerived(Base1, Base2):
            def test_access(self):
                return {
                    # Base1 members are private (from private inheritance)
                    'base1_public': self.base1_public(),  # Internal access works
                    'base1_protected': self.base1_protected(),
                    
                    # Base2 members follow protected inheritance rules
                    'base2_public': self.base2_public(),  # Internal access works
                    'base2_protected': self.base2_protected()
                }
        
        multi_obj = MultiDerived()
        
        # Internal access should work
        results = multi_obj.test_access()
        assert results['base1_public'] == 'base1_public'
        assert results['base1_protected'] == 'base1_protected'
        assert results['base2_public'] == 'base2_public'
        assert results['base2_protected'] == 'base2_protected'
        
        # External access should be blocked due to inheritance types
        with pytest.raises(PermissionDeniedError):
            multi_obj.base1_public()  # Private inheritance
        
        with pytest.raises(PermissionDeniedError):
            multi_obj.base2_public()  # Protected inheritance
    
    def test_deep_inheritance_chain(self):
        """Test inheritance through multiple levels"""
        class GrandParent:
            @protected
            def grandparent_method(self):
                return "grandparent_protected"
        
        class Parent(GrandParent):
            @protected
            def parent_method(self):
                return "parent_protected"
        
        @private(Parent)
        class Child(Parent):
            def test_access(self):
                return {
                    'grandparent': self.grandparent_method(),
                    'parent': self.parent_method()
                }
        
        child_obj = Child()
        
        # Internal access should work
        results = child_obj.test_access()
        assert results['grandparent'] == 'grandparent_protected'
        assert results['parent'] == 'parent_protected'
        
        # External access should be blocked due to private inheritance from Parent
        with pytest.raises(PermissionDeniedError):
            child_obj.grandparent_method()
        
        with pytest.raises(PermissionDeniedError):
            child_obj.parent_method()


@pytest.mark.inheritance
@pytest.mark.cpp_semantics
class TestInheritanceTypeEnforcement:
    """Test that inheritance types are properly enforced"""
    
    def test_inheritance_type_detection(self):
        """Test that inheritance types work correctly through behavior verification"""
        class Base:
            @protected
            def protected_method(self):
                return "base_protected"
            
            def public_method(self):
                return "base_public"
        
        @private(Base)
        class PrivateDerived(Base):
            def test_internal_access(self):
                # Private inheritance - can access from within class
                return {
                    'protected': self.protected_method(),  # Should work internally
                    'public': self.public_method()  # Should work internally
                }
        
        @protected(Base)
        class ProtectedDerived(Base):
            def test_internal_access(self):
                # Protected inheritance - can access from within class
                return {
                    'protected': self.protected_method(),
                    'public': self.public_method()
                }
        
        class PublicDerived(Base):  # Default is public
            def test_internal_access(self):
                return {
                    'protected': self.protected_method(),
                    'public': self.public_method()
                }
        
        # Test behavior differences
        private_obj = PrivateDerived()
        protected_obj = ProtectedDerived()
        public_obj = PublicDerived()
        
        # All should work internally
        assert private_obj.test_internal_access()['protected'] == "base_protected"
        assert protected_obj.test_internal_access()['protected'] == "base_protected"
        assert public_obj.test_internal_access()['protected'] == "base_protected"
        
        # External access should differ based on inheritance type
        # Private inheritance - no external access to inherited methods
        with pytest.raises(PermissionDeniedError):
            private_obj.public_method()
        
        # Protected inheritance - no external access to any inherited methods
        with pytest.raises(PermissionDeniedError):
            protected_obj.public_method()
        
        # Public inheritance - external access to public methods should work
        assert public_obj.public_method() == "base_public"
    
    def test_inheritance_info_storage(self):
        """Test that inheritance information is properly stored"""
        class Base1:
            pass
        
        class Base2:
            pass
        
        @private(Base1)
        @protected(Base2)
        class MultiInheritance(Base1, Base2):
            pass
        
        # Check that inheritance info is stored
        assert hasattr(MultiInheritance, '_inheritance_info')
        assert MultiInheritance._inheritance_info['Base1'] == InheritanceType.PRIVATE.value
        assert MultiInheritance._inheritance_info['Base2'] == InheritanceType.PROTECTED.value
