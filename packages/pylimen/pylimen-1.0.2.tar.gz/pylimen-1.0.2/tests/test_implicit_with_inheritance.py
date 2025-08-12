#!/usr/bin/env python3
"""
Test implicit access control with inheritance decorators
"""

from limen import private, protected, public
from limen.exceptions import PermissionDeniedError

print("Testing Implicit Access Control with Inheritance...\n")

# Test: Base class with naming-based implicit access control
print("=== Base Class (should have implicit access control) ===")

class Base:
    def implicit_public_method(self):
        return "implicit public"
    
    def _implicit_protected_method(self):
        return "implicit protected"
    
    def __implicit_private_method(self):
        return "implicit private"
    
    @public
    def explicit_public_method(self):
        return "explicit public"
        
    @private
    def explicit_private_method(self):
        return "explicit private"
        
    @protected
    def explicit_protected_method(self):
        return "explicit protected"

# Test Base class before applying inheritance decorator
print("Before any decoration:")
base_obj = Base()

# Test implicit public (should work - no implicit control applied yet)
try:
    result = base_obj.implicit_public_method()
    print(f"  implicit_public_method: {result} (should work)")
except PermissionDeniedError as e:
    print(f"  implicit_public_method: BLOCKED - {e}")

# Test implicit protected (should work - no implicit control applied yet)
try:
    result = base_obj._implicit_protected_method()
    print(f"  _implicit_protected_method: {result} (should work - no implicit control yet)")
except PermissionDeniedError as e:
    print(f"  _implicit_protected_method: BLOCKED - {e}")

# Test explicit protected (should be blocked)
try:
    result = base_obj.explicit_protected_method()
    print(f"  explicit_protected_method: {result} (should be blocked)")
except PermissionDeniedError as e:
    print(f"  explicit_protected_method: BLOCKED - {e}")

print("\n=== Now applying @protected(Base) inheritance decorator ===")

@protected(Base)
class Derived(Base):
    def test_internal_access(self):
        """Test what derived class can access internally"""
        results = {}
        
        # Test implicit methods
        try:
            results['implicit_public'] = self.implicit_public_method()
        except Exception as e:
            results['implicit_public'] = f"Error: {e}"
        
        try:
            results['implicit_protected'] = self._implicit_protected_method()
        except Exception as e:
            results['implicit_protected'] = f"Error: {e}"
        
        try:
            results['implicit_private'] = self._Base__implicit_private_method()
        except Exception as e:
            results['implicit_private'] = f"Error: {e}"
        
        # Test explicit methods
        try:
            results['explicit_public'] = self.explicit_public_method()
        except Exception as e:
            results['explicit_public'] = f"Error: {e}"
        
        try:
            results['explicit_protected'] = self.explicit_protected_method()
        except Exception as e:
            results['explicit_protected'] = f"Error: {e}"
        
        try:
            results['explicit_private'] = self.explicit_private_method()
        except Exception as e:
            results['explicit_private'] = f"Error: {e}"
        
        return results

derived_obj = Derived()

print("Internal access from Derived class:")
internal_results = derived_obj.test_internal_access()
for method, result in internal_results.items():
    print(f"  {method}: {result}")

print("\nExternal access to Derived object:")

# Test external access to implicit methods
print("Implicit methods:")
try:
    result = derived_obj.implicit_public_method()
    print(f"  ❌ implicit_public_method: {result} (should be blocked due to protected inheritance)")
except PermissionDeniedError as e:
    print(f"  ✅ implicit_public_method: BLOCKED - {e}")

try:
    result = derived_obj._implicit_protected_method()
    print(f"  ❌ _implicit_protected_method: {result} (should be blocked)")
except PermissionDeniedError as e:
    print(f"  ✅ _implicit_protected_method: BLOCKED - {e}")

# Test external access to explicit methods
print("Explicit methods:")
try:
    result = derived_obj.explicit_public_method()
    print(f"  ❌ explicit_public_method: {result} (should be blocked due to protected inheritance)")
except PermissionDeniedError as e:
    print(f"  ✅ explicit_public_method: BLOCKED - {e}")

try:
    result = derived_obj.explicit_protected_method()
    print(f"  ❌ explicit_protected_method: {result} (should be blocked)")
except PermissionDeniedError as e:
    print(f"  ✅ explicit_protected_method: BLOCKED - {e}")

print("\n=== Key Questions ===")
print("1. Does @protected(Base) apply implicit access control to Base class methods?")
print("2. Do underscore methods get treated as protected automatically?")
print("3. Do double underscore methods get treated as private automatically?")
print("4. Do explicit decorators override implicit naming conventions?")
