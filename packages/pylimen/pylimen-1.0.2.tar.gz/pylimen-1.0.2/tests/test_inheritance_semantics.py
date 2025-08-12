#!/usr/bin/env python3
"""
Test C++ style inheritance semantics
"""

from limen import private, protected, public
from limen.exceptions import PermissionDeniedError
from limen.utils.implicit import apply_implicit_access_control

print("Testing C++ Style Inheritance Semantics...\n")

# Test 1: Protected Inheritance - Public becomes Protected
print("=== Test 1: Protected Inheritance (Public → Protected) ===")

class Base:
    def public_method(self):
        return "base public"
    
    def _protected_method(self):
        return "base protected"
    
    def __private_method(self):
        return "base private"
    
    @public
    def explicit_public(self):
        return "explicit public"
    
    @protected
    def explicit_protected(self):
        return "explicit protected"
    
    @private
    def explicit_private(self):
        return "explicit private"

# Apply implicit access control to Base
apply_implicit_access_control(Base)

@protected(Base)
class ProtectedDerived(Base):
    def test_inherited_access(self):
        """Test what the derived class can access"""
        results = {}
        try:
            results['public_method'] = self.public_method()
        except Exception as e:
            results['public_method'] = f"Error: {e}"
        
        try:
            results['_protected_method'] = self._protected_method()
        except Exception as e:
            results['_protected_method'] = f"Error: {e}"
        
        try:
            results['explicit_public'] = self.explicit_public()
        except Exception as e:
            results['explicit_public'] = f"Error: {e}"
        
        try:
            results['explicit_protected'] = self.explicit_protected()
        except Exception as e:
            results['explicit_protected'] = f"Error: {e}"
        
        return results

# Test inheritance behavior
obj = ProtectedDerived()

print("=== Internal Access (from derived class) ===")
internal_results = obj.test_inherited_access()
for method, result in internal_results.items():
    print(f"  {method}: {result}")

print("\n=== External Access (from outside) ===")

# Test external access to original public method (should now be protected)
try:
    result = obj.public_method()
    print(f"  ❌ public_method: {result} (should be blocked due to protected inheritance)")
except PermissionDeniedError as e:
    print(f"  ✅ public_method: Correctly blocked - {e}")

# Test external access to originally protected method (should remain protected)
try:
    result = obj._protected_method()
    print(f"  ❌ _protected_method: {result} (should be blocked)")
except PermissionDeniedError as e:
    print(f"  ✅ _protected_method: Correctly blocked - {e}")

# Test external access to explicit public (should become protected)
try:
    result = obj.explicit_public()
    print(f"  ❌ explicit_public: {result} (should be blocked due to protected inheritance)")
except PermissionDeniedError as e:
    print(f"  ✅ explicit_public: Correctly blocked - {e}")

# Test external access to explicit protected (should remain protected)
try:
    result = obj.explicit_protected()
    print(f"  ❌ explicit_protected: {result} (should be blocked)")
except PermissionDeniedError as e:
    print(f"  ✅ explicit_protected: Correctly blocked - {e}")

print("\n=== Test 2: Compare with Normal (Public) Inheritance ===")

class PublicDerived(Base):
    def test_inherited_access(self):
        """Test normal inheritance"""
        results = {}
        try:
            results['public_method'] = self.public_method()
        except Exception as e:
            results['public_method'] = f"Error: {e}"
        
        try:
            results['explicit_public'] = self.explicit_public()
        except Exception as e:
            results['explicit_public'] = f"Error: {e}"
        
        return results

obj2 = PublicDerived()

print("=== External Access (normal inheritance) ===")

# Test external access with normal inheritance (should work for public)
try:
    result = obj2.public_method()
    print(f"  ✅ public_method: {result} (accessible with normal inheritance)")
except PermissionDeniedError as e:
    print(f"  ❌ public_method: Should be accessible - {e}")

try:
    result = obj2.explicit_public()
    print(f"  ✅ explicit_public: {result} (accessible with normal inheritance)")
except PermissionDeniedError as e:
    print(f"  ❌ explicit_public: Should be accessible - {e}")

print("\n=== Summary ===")
print("Protected inheritance should:")
print("  - Convert public methods to protected (block external access)")
print("  - Keep protected methods as protected")
print("  - Keep private methods as private")
print("  - Allow derived class to access all inherited members")
