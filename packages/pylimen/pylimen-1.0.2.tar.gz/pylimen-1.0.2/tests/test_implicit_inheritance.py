#!/usr/bin/env python3
"""
Test implicit access control with inheritance decorators
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from limen import protected, private, public
from limen.exceptions import PermissionDeniedError

def test_implicit_inheritance():
    """Test implicit access control when using inheritance decorators"""
    
    print("=== Testing Implicit Access Control with Inheritance ===\n")
    
    # Define base class with mixed implicit/explicit methods
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
    
    print("Base class methods:")
    base_obj = Base()
    
    # Test base class access
    try:
        print(f"  ✅ implicit_public_method: {base_obj.implicit_public_method()}")
    except Exception as e:
        print(f"  ❌ implicit_public_method failed: {e}")
    
    try:
        print(f"  ? _implicit_protected_method: {base_obj._implicit_protected_method()}")
    except PermissionDeniedError as e:
        print(f"  ✅ _implicit_protected_method blocked: {e}")
    except Exception as e:
        print(f"  ❌ _implicit_protected_method error: {e}")
    
    try:
        print(f"  ✅ explicit_public_method: {base_obj.explicit_public_method()}")
    except Exception as e:
        print(f"  ❌ explicit_public_method failed: {e}")
    
    try:
        print(f"  ? explicit_private_method: {base_obj.explicit_private_method()}")
    except PermissionDeniedError as e:
        print(f"  ✅ explicit_private_method blocked: {e}")
    except Exception as e:
        print(f"  ❌ explicit_private_method error: {e}")
    
    print("\n" + "="*50)
    
    # Now test with inheritance decorator
    @protected(Base)
    class Derived(Base):
        def test_inherited_access(self):
            """Test if derived class can access inherited methods properly"""
            results = {}
            
            try:
                results['implicit_public'] = self.implicit_public_method()
            except Exception as e:
                results['implicit_public'] = f"FAILED: {e}"
            
            try:
                results['implicit_protected'] = self._implicit_protected_method()
            except Exception as e:
                results['implicit_protected'] = f"FAILED: {e}"
            
            try:
                results['implicit_private'] = self._Base__implicit_private_method()
            except Exception as e:
                results['implicit_private'] = f"FAILED: {e}"
            
            try:
                results['explicit_public'] = self.explicit_public_method()
            except Exception as e:
                results['explicit_public'] = f"FAILED: {e}"
            
            try:
                results['explicit_protected'] = self.explicit_protected_method()
            except Exception as e:
                results['explicit_protected'] = f"FAILED: {e}"
            
            try:
                results['explicit_private'] = self.explicit_private_method()
            except Exception as e:
                results['explicit_private'] = f"FAILED: {e}"
            
            return results
    
    print("Derived class internal access:")
    derived_obj = Derived()
    internal_results = derived_obj.test_inherited_access()
    
    for method_name, result in internal_results.items():
        if "FAILED" in str(result):
            print(f"  ❌ {method_name}: {result}")
        else:
            print(f"  ✅ {method_name}: {result}")
    
    print("\nDerived class external access:")
    
    # Test external access to derived class
    try:
        print(f"  ✅ implicit_public_method: {derived_obj.implicit_public_method()}")
    except Exception as e:
        print(f"  ❌ implicit_public_method failed: {e}")
    
    try:
        result = derived_obj._implicit_protected_method()
        print(f"  ❌ _implicit_protected_method should be blocked: {result}")
    except PermissionDeniedError as e:
        print(f"  ✅ _implicit_protected_method blocked: {e}")
    except Exception as e:
        print(f"  ❌ _implicit_protected_method error: {e}")
    
    try:
        print(f"  ✅ explicit_public_method: {derived_obj.explicit_public_method()}")
    except Exception as e:
        print(f"  ❌ explicit_public_method failed: {e}")
    
    try:
        result = derived_obj.explicit_private_method()
        print(f"  ❌ explicit_private_method should be blocked: {result}")
    except PermissionDeniedError as e:
        print(f"  ✅ explicit_private_method blocked: {e}")
    except Exception as e:
        print(f"  ❌ explicit_private_method error: {e}")

if __name__ == "__main__":
    test_implicit_inheritance()
