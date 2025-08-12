"""
Test file to demonstrate and fix decorator usage validation issues
"""
import pytest

# Import from the limen package
from limen import private, protected
from limen.exceptions import DecoratorUsageError


def test_invalid_bare_class_decoration():
    """Test that bare class decoration (without arguments) raises an error"""
    
    # This should raise an error - bare decoration on class is invalid
    with pytest.raises(DecoratorUsageError, match="cannot be applied to a class without specifying a class"):
        @private
        class InvalidClass:
            pass


def test_valid_inheritance_decoration():
    """Test that inheritance decoration works correctly"""
    
    class Base:
        def method(self):
            return "base"
    
    # This should work - inheritance decoration with arguments
    @private(Base)
    class ValidDerived:
        pass
    
    # Should create inheritance decorator successfully
    assert hasattr(ValidDerived, '_inheritance_info')


def test_valid_multiple_inheritance_decoration():
    """Test that multiple inheritance decoration works"""
    
    class Base1:
        pass
    
    class Base2:
        pass
    
    # This should work - multiple inheritance
    @protected(Base1, Base2)
    class ValidMultipleDerived:
        pass
    
    assert hasattr(ValidMultipleDerived, '_inheritance_info')


def test_valid_method_decoration():
    """Test that method decoration works"""
    
    class TestClass:
        @private
        def valid_method(self):
            return "valid"
    
    # Should create method descriptor
    assert hasattr(TestClass.valid_method, '__get__')


def test_invalid_function_decoration():
    """Test that module-level function decoration raises error"""
    
    with pytest.raises(DecoratorUsageError, match="cannot be applied to module-level function"):
        @private
        def invalid_function():
            pass


if __name__ == "__main__":
    # Run the invalid cases to see current behavior
    print("Testing current behavior...")
    
    try:
        print("Testing bare class decoration...")
        @private
        class TestBareClass:
            pass
        print("UNEXPECTED: Bare class decoration did not raise error!")
    except Exception as e:
        print(f"EXPECTED: {e}")
    
    try:
        print("\nTesting inheritance decoration...")
        class Base:
            pass
        
        @private(Base)
        class TestInheritanceClass:
            pass
        print("EXPECTED: Inheritance decoration worked!")
    except Exception as e:
        print(f"UNEXPECTED: {e}")
    
    try:
        print("\nTesting method decoration...")
        class TestMethodClass:
            @private
            def test_method(self):
                pass
        print("EXPECTED: Method decoration worked!")
    except Exception as e:
        print(f"UNEXPECTED: {e}")
    
    try:
        print("\nTesting function decoration...")
        @private
        def test_function():
            pass
        print("UNEXPECTED: Function decoration did not raise error!")
    except Exception as e:
        print(f"EXPECTED: {e}")
