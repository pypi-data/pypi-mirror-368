"""
Test the fixed decorator validation logic
"""
import sys
import os

# Add current directory to path and try to import the modules directly
sys.path.insert(0, os.path.dirname(__file__))

# Import the core components we need
try:
    from core.enums import AccessLevel
    from decorators.base import AccessControlDecorator
    print("Successfully imported components!")
    
    # Test the logic
    def test_decorator_validation():
        print("\n=== Testing Decorator Validation ===")
        
        # Test 1: Valid method decoration
        print("\n--- Test 1: Method decoration (should work) ---")
        decorator = AccessControlDecorator(AccessLevel.PRIVATE)
        
        def test_method():
            pass
        
        try:
            result = decorator(test_method)
            print("✓ Method decoration successful")
        except Exception as e:
            print(f"✗ Method decoration failed: {e}")
        
        # Test 2: Valid inheritance decoration (simulated)
        print("\n--- Test 2: Inheritance decoration (should work) ---")
        class Base:
            pass
        
        try:
            # This simulates @private(Base) which should return a decorator
            inheritance_decorator = decorator(Base)
            print("✓ Inheritance decorator creation successful")
            
            # Now apply it to a derived class (this is what the decorator would do)
            if callable(inheritance_decorator):
                class Derived:
                    pass
                result = inheritance_decorator(Derived)
                print("✓ Inheritance decoration application successful")
        except Exception as e:
            print(f"✗ Inheritance decoration failed: {e}")
        
        # Test 3: Invalid bare class decoration
        print("\n--- Test 3: Bare class decoration (should fail) ---")
        try:
            @decorator  # This should be detected as invalid
            class TestClass:
                pass
            print("✗ Bare class decoration unexpectedly succeeded")
        except ValueError as e:
            print(f"✓ Bare class decoration correctly rejected: {e}")
        except Exception as e:
            print(f"? Bare class decoration failed with unexpected error: {e}")
        
        print("\n=== Test Complete ===")
    
    if __name__ == "__main__":
        test_decorator_validation()
        
except ImportError as e:
    print(f"Import failed: {e}")
    print("Cannot run tests due to import issues")
    
    # Fallback: just test that our changes don't break the file syntax
    try:
        from decorators import base
        print("At least the decorators.base module loads without syntax errors")
    except Exception as e2:
        print(f"Syntax error in decorators.base: {e2}")
