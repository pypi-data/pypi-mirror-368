#!/usr/bin/env python3
"""
Test if base class gets implicit access control when inheritance decorator is used
"""

from limen import private, protected, public
from limen.exceptions import PermissionDeniedError

print("Testing Base Class Implicit Access Control After Inheritance Decorator...\n")

class Base:
    def implicit_public_method(self):
        return "implicit public"
    
    def _implicit_protected_method(self):
        return "implicit protected"
    
    def __implicit_private_method(self):
        return "implicit private"

print("=== Before applying inheritance decorator ===")
base_obj = Base()

try:
    result = base_obj._implicit_protected_method()
    print(f"_implicit_protected_method: {result} (should work - no implicit control yet)")
except PermissionDeniedError as e:
    print(f"_implicit_protected_method: BLOCKED - {e}")

print("\n=== Applying @protected(Base) - this should trigger implicit access control on Base ===")

@protected(Base)
class Derived(Base):
    pass

print("\n=== Testing Base class again (should now have implicit access control) ===")

try:
    result = base_obj._implicit_protected_method()
    print(f"❌ _implicit_protected_method: {result} (should be blocked now)")
except PermissionDeniedError as e:
    print(f"✅ _implicit_protected_method: BLOCKED - {e}")

try:
    result = base_obj.implicit_public_method()
    print(f"✅ implicit_public_method: {result} (should still work - public)")
except PermissionDeniedError as e:
    print(f"❌ implicit_public_method: BLOCKED - {e} (shouldn't be blocked)")

try:
    result = base_obj._Base__implicit_private_method()
    print(f"❌ __implicit_private_method: {result} (should be blocked)")
except PermissionDeniedError as e:
    print(f"✅ __implicit_private_method: BLOCKED - {e}")

print("\n=== Testing new Base instance ===")
new_base = Base()

try:
    result = new_base._implicit_protected_method()
    print(f"❌ _implicit_protected_method (new instance): {result} (should be blocked)")
except PermissionDeniedError as e:
    print(f"✅ _implicit_protected_method (new instance): BLOCKED - {e}")

print("\n✅ SUCCESS: Implicit access control is now applied to base classes when inheritance decorators are used!")
