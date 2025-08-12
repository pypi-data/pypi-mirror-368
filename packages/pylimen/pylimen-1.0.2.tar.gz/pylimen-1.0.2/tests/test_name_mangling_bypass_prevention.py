"""
Test Name Mangling Bypass Prevention

This test suite verifies that Limen properly prevents bypassing access control
through Python's name mangling mechanism. It ensures that private methods cannot
be accessed externally via `obj._ClassName__method()` syntax while preserving
legitimate internal access and friend relationships.
"""

import pytest
from limen.exceptions import PermissionDeniedError
from limen.decorators import private, friend
from limen.utils.implicit import apply_implicit_access_control


class TestNameManglingBypassPrevention:
    """Test that name mangling bypasses are properly prevented for private methods"""

    def test_implicit_private_method_basic_behavior(self):
        """Test basic behavior of implicit private methods"""

        class TestClass:
            def __private_method(self):
                return "private_data"

            def internal_access(self):
                # Internal access should work
                return self.__private_method()

        # Apply implicit access control
        apply_implicit_access_control(TestClass)

        obj = TestClass()

        # Internal access should work
        assert obj.internal_access() == "private_data"

        # Direct access should fail (AttributeError because __private_method doesn't exist)
        with pytest.raises(AttributeError):
            obj.__private_method()

    def test_implicit_private_method_name_mangling_blocked(self):
        """Test that implicit private methods cannot be bypassed with name mangling"""

        class TestClass:
            def __private_method(self):
                return "private_data"

            def internal_access(self):
                # Internal access should work
                return self.__private_method()

        # Apply implicit access control
        apply_implicit_access_control(TestClass)

        obj = TestClass()

        # Internal access should work
        assert obj.internal_access() == "private_data"

        # Name mangling bypass should be blocked
        with pytest.raises(PermissionDeniedError, match="Access denied to private method"):
            obj._TestClass__private_method()

    def test_explicit_private_method_basic_behavior(self):
        """Test basic behavior of explicit @private methods"""

        class TestClass:
            @private
            def private_method(self):
                return "explicit_private"

            def internal_access(self):
                return self.private_method()

        obj = TestClass()

        # Internal access should work
        assert obj.internal_access() == "explicit_private"

        # Direct access should be blocked
        with pytest.raises(PermissionDeniedError, match="Access denied to private method"):
            obj.private_method()

    def test_friend_access_works(self):
        """Test that friend access still works"""

        class Target:
            def __private_method(self):
                return "target_private"

        @friend(Target)
        class Friend:
            def access_target(self, target):
                # Friend should be able to access via the mangled name
                return target._Target__private_method()

        # Apply implicit access control
        apply_implicit_access_control(Target)

        target = Target()
        friend_obj = Friend()

        # Friend access should work
        result = friend_obj.access_target(target)
        assert result == "target_private"

    def test_enforcement_disabled_allows_access(self):
        """Test that disabling enforcement allows access"""

        class TestClass:
            def __private_method(self):
                return "bypassed"

        # Apply implicit access control
        apply_implicit_access_control(TestClass)

        obj = TestClass()

        # Disable enforcement
        from limen.system.access_control import get_access_control_system
        access_control = get_access_control_system()
        original_enforcement = access_control.enforcement_enabled
        access_control.enforcement_enabled = False

        try:
            # Access should work when enforcement is disabled
            result = obj._TestClass__private_method()
            assert result == "bypassed"
        finally:
            # Restore enforcement
            access_control.enforcement_enabled = original_enforcement

    def test_name_mangling_bypass_specifically_blocked(self):
        """Test specifically that name mangling bypasses are blocked"""

        class OuterClass:
            """Use a nested class to ensure name mangling works properly"""
            
            class TestClass:
                def __private_method(self):
                    return "private_data"

                def internal_access(self):
                    return self.__private_method()

        # Apply implicit access control
        apply_implicit_access_control(OuterClass.TestClass)

        obj = OuterClass.TestClass()

        # Internal access should work
        assert obj.internal_access() == "private_data"

        # Name mangling bypass should be blocked (the exact error message may vary)
        with pytest.raises(PermissionDeniedError, match="Access denied to private method"):
            obj._TestClass__private_method()
