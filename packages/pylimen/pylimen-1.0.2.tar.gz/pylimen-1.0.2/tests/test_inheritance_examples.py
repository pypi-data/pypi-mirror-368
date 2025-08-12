#!/usr/bin/env python3
"""
Test various inheritance patterns and friend function functionality
"""

from limen import private, protected, public, friend
from limen.exceptions import PermissionDeniedError

print("Testing inheritance patterns...\n")

# Test 1: Multiple inheritance with access control
print("=== Test 1: Multiple Inheritance ===")
try:
    class Base1:
        def base1_method(self):
            return "base1 method"
    
    class Base2:
        def base2_method(self):
            return "base2 method"
    
    @protected(Base1, Base2)
    class MultiDerived(Base1, Base2):
        def test_access(self):
            return f"{self.base1_method()}, {self.base2_method()}"
    
    obj = MultiDerived()
    print(f"✅ Multiple inheritance works: {obj.test_access()}")
    
    # Test external access (should be blocked due to protected inheritance)
    try:
        obj.base1_method()
        print("❌ External access to base1_method should be blocked")
    except PermissionDeniedError:
        print("✅ External access to base1_method correctly blocked")
        
except Exception as e:
    print(f"❌ Multiple inheritance failed: {e}")

print()

# Test 2: Protected class inheritance 
print("=== Test 2: Protected Class Access ===")
try:
    class Base:
        @protected
        def protected_method(self):
            return "protected method"
    
    @protected(Base)
    class Derived(Base):
        def public_method(self):
            # Should be able to access inherited protected method
            return self.protected_method()
    
    obj = Derived()
    result = obj.public_method()
    print(f"✅ Protected inheritance works: {result}")
    
    # Test external access to inherited method (should be blocked)
    try:
        obj.protected_method()
        print("❌ External access to protected_method should be blocked")
    except PermissionDeniedError:
        print("✅ External access to protected_method correctly blocked")
        
except Exception as e:
    print(f"❌ Protected class inheritance failed: {e}")

print()

# Test 3: Friend functions (standalone functions)
print("=== Test 3: Friend Functions ===")
try:
    class SecureBox:
        def __init__(self, secret):
            self._secret = secret
        
        @private
        def get_secret(self):
            return self._secret
    
    @friend(SecureBox)
    def authorized_backup(box):
        """Standalone friend function"""
        return f"Backup: {box.get_secret()}"
    
    @friend(SecureBox) 
    def security_scan(box):
        """Another standalone friend function"""
        return f"Scan: {box.get_secret()}"
    
    def unauthorized_attempt(box):
        """Regular function - no friend access"""
        return box.get_secret()
    
    box = SecureBox("top_secret_data")
    
    # Test friend functions
    backup_result = authorized_backup(box)
    scan_result = security_scan(box)
    print(f"✅ Friend function 1: {backup_result}")
    print(f"✅ Friend function 2: {scan_result}")
    
    # Test unauthorized function
    try:
        unauthorized_attempt(box)
        print("❌ Unauthorized function should be blocked")
    except PermissionDeniedError:
        print("✅ Unauthorized function correctly blocked")
        
except Exception as e:
    print(f"❌ Friend functions failed: {e}")

print()

# Test 4: Implicit access control
print("=== Test 4: Implicit Access Control ===")
try:
    @protected  # Apply to class to enable implicit access control
    class ImplicitExample:
        def public_method(self):
            return "public"
        
        def _protected_method(self):
            return "protected"
        
        def __private_method(self):
            return "private"
        
        def test_internal_access(self):
            return {
                'public': self.public_method(),
                'protected': self._protected_method(),
                'private': self.__private_method()
            }
    
    obj = ImplicitExample()
    
    # Test internal access
    internal_results = obj.test_internal_access()
    print(f"✅ Internal access works: {internal_results}")
    
    # Test external access to public (should work)
    try:
        public_result = obj.public_method()
        print(f"✅ External public access: {public_result}")
    except PermissionDeniedError:
        print("❌ Public method should be accessible externally")
    
    # Test external access to protected (should be blocked)
    try:
        obj._protected_method()
        print("❌ External protected access should be blocked")
    except PermissionDeniedError:
        print("✅ External protected access correctly blocked")
    
    # Test external access to private (should be blocked)
    try:
        obj._ImplicitExample__private_method()  # Python name mangling
        print("❌ External private access should be blocked")
    except PermissionDeniedError:
        print("✅ External private access correctly blocked")
        
except Exception as e:
    print(f"❌ Implicit access control failed: {e}")

print()

# Test 5: Override implicit with explicit decorators
print("=== Test 5: Override Implicit with Explicit ===")
try:
    @protected  # Apply to class to enable implicit access control
    class OverrideExample:
        def _normally_protected(self):
            return "would be protected"
        
        @public
        def _explicitly_public(self):
            return "explicitly made public"
        
        @private  
        def normally_public(self):
            return "explicitly made private"
    
    obj = OverrideExample()
    
    # Test that explicit @public overrides implicit protected
    try:
        result = obj._explicitly_public()
        print(f"✅ Explicit @public override: {result}")
    except PermissionDeniedError:
        print("❌ Explicit @public should override implicit protected")
    
    # Test that explicit @private overrides implicit public
    try:
        obj.normally_public()
        print("❌ Explicit @private should block access")
    except PermissionDeniedError:
        print("✅ Explicit @private correctly overrides implicit public")
        
except Exception as e:
    print(f"❌ Explicit override failed: {e}")

print("\n=== Summary ===")
print("If all tests show ✅, then the functionality is working correctly!")
