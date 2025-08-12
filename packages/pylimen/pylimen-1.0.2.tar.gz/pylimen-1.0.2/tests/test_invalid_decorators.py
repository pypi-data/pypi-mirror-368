#!/usr/bin/env python3
"""
Test invalid decorator combinations that should throw errors
"""
import pytest
from limen import private, protected, public
from limen.exceptions import DecoratorUsageError, DecoratorConflictError

def test_multiple_access_decorators_on_method():
    """Test that multiple access decorators on same method throw error"""
    
    with pytest.raises(DecoratorConflictError, match="Conflicting access level decorators on.*already has"):
        class TestClass:
            @private
            @protected  # Should error - multiple access decorators
            def method(self):
                pass

def test_multiple_access_decorators_on_property():
    """Test that multiple access decorators on property throw error"""
    
    with pytest.raises(DecoratorConflictError, match="was applied to.*more than once"):
        class TestClass:
            @private
            @property
            @private  # Should error - multiple access decorators
            def prop(self):
                return "test"

def test_multiple_access_decorators_on_staticmethod():
    """Test that multiple access decorators on staticmethod throw error"""
    
    with pytest.raises(DecoratorConflictError, match="Conflicting access level decorators on.*already has"):
        class TestClass:
            @protected
            @staticmethod
            @private  # Should error - multiple access decorators
            def static_method():
                pass

def test_inheritance_decorator_on_method():
    """Test that inheritance decorators on methods throw error"""
    
    class Base:
        pass
    
    with pytest.raises(DecoratorUsageError, match="cannot be applied to method"):
        class TestClass:
            @private(Base)  # Should error - inheritance on method
            def method(self):
                pass

def test_inheritance_decorator_on_function():
    """Test that inheritance decorators on module functions throw error"""
    
    class Base:
        pass
    
    with pytest.raises(DecoratorUsageError, match="cannot be applied to method"):
        @private(Base)  # Should error - inheritance on function
        def function():
            pass

def test_access_decorator_on_module_function():
    """Test that access decorators on module functions throw error"""
    
    with pytest.raises(DecoratorUsageError, match="cannot be applied to module-level function"):
        @private  # Should error - access control on module function
        def function():
            pass

def test_hanging_decorator():
    """Test hanging/incomplete decorator syntax (should error)"""
    
    class Base:
        pass
    
    # This should error - hanging @private with no arguments on class
    with pytest.raises(DecoratorUsageError, match="cannot be applied to a class without specifying a class"):
        @private  # Hanging decorator - no inheritance specified
        @private(Base)  # Valid decorator after invalid one
        class InvalidHanging:
            pass

def test_sandwiched_invalid_decorator():
    """Test invalid decorator sandwiched between valid ones"""
    
    class Base1:
        pass
    class Base2:
        pass
    class Base3:
        pass
    
    # This should error - bare @protected sandwiched between inheritance decorators
    with pytest.raises(DecoratorUsageError, match="cannot be applied to a class without specifying a class"):
        @private(Base1, Base2)
        @protected  # Invalid - bare decorator between inheritance decorators
        @protected(Base3)
        class InvalidSandwiched:
            pass
    """Test multiple inheritance decorators (should be VALID like C++)"""
    
    class Base1:
        pass
    class Base2:
        pass
    class Base3:
        pass
    
    # This should be valid - multiple inheritance with same access type
    @private(Base1, Base2)
    class ValidSameType:
        pass
    
    # This should ALSO be valid - multiple inheritance with different access types (like C++)
    @private(Base1)
    @protected(Base2)
    @public(Base3)  # This should be valid - mixed inheritance like C++
    class ValidMixedTypes:
        pass
    
    # Verify the inheritance info is set correctly
    assert hasattr(ValidMixedTypes, '_inheritance_info')
    expected_info = {
        'Base1': 'private',
        'Base2': 'protected', 
        'Base3': 'public'
    }
    assert ValidMixedTypes._inheritance_info == expected_info
    print("✅ Multiple inheritance with different access types works correctly!")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
