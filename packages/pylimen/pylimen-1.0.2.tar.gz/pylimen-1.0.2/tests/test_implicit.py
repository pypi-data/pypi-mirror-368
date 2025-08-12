#!/usr/bin/env python3
"""
Test implicit access control functionality
"""

from limen.utils.implicit import apply_implicit_access_control
from limen.utils.naming import detect_implicit_access_level

# Test naming detection
print('Testing naming detection:')
print('public_method ->', detect_implicit_access_level('public_method'))
print('_protected_method ->', detect_implicit_access_level('_protected_method'))
print('__private_method ->', detect_implicit_access_level('__private_method'))
print('__init__ ->', detect_implicit_access_level('__init__'))

# Test implicit access control
print('\nTesting implicit access control:')
class TestClass:
    def public_method(self):
        return 'public'
    
    def _protected_method(self):
        return 'protected'
    
    def __private_method(self):
        return 'private'
    
    def test_internal(self):
        return {
            'public': self.public_method(),
            'protected': self._protected_method(), 
            'private': self.__private_method()
        }

# Apply implicit access control
apply_implicit_access_control(TestClass)

obj = TestClass()
print('Internal access:', obj.test_internal())

# Test external access
try:
    print('External public:', obj.public_method())
except Exception as e:
    print('Public blocked:', e)

try:
    obj._protected_method()
    print('Protected accessible externally (should be blocked)')
except Exception as e:
    print('Protected blocked:', str(e)[:50])

try:
    obj._TestClass__private_method()
    print('Private accessible externally (should be blocked)')
except Exception as e:
    print('Private blocked:', str(e)[:50])
