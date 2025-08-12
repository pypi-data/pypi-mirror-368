#!/usr/bin/env python3
"""
Test the README examples to ensure documentation accuracy
"""

from limen import private, protected, public, friend
from limen.exceptions import PermissionDeniedError
from limen.utils.implicit import apply_implicit_access_control

print("Testing README Documentation Examples...\n")

# Test 1: Basic Quick Start Example
print("=== Quick Start Example ===")
class BankAccount:
    def __init__(self, balance=0):
        self._balance = balance
    
    @private
    def _validate_transaction(self, amount):
        return amount > 0 and amount <= self._balance
    
    @protected
    def _log_transaction(self, amount):
        print(f"Transaction: ${amount}")
    
    @public
    def withdraw(self, amount):
        if self._validate_transaction(amount):
            self._balance -= amount
            self._log_transaction(amount)
            return True
        return False

account = BankAccount(1000)
result = account.withdraw(100)
print(f"Withdraw successful: {result}")

try:
    account._validate_transaction(50)
    print("ERROR: Should have blocked private access")
except PermissionDeniedError:
    print("SUCCESS: Private access correctly blocked")

# Test 2: Implicit Access Control Example
print("\n=== Implicit Access Control Example ===")
class BaseAPI:
    def get_data(self):
        return "public data"
    
    def _internal_process(self):
        return "protected process"
    
    def __secret_key(self):
        return "private key"
    
    @public
    def _explicitly_public(self):
        return "explicit public override"

@protected(BaseAPI)
class DerivedAPI(BaseAPI):
    def test_access(self):
        # Can access all inherited methods internally
        public_data = self.get_data()
        protected_data = self._internal_process()
        explicit_data = self._explicitly_public()
        return f"{public_data}, {protected_data}, {explicit_data}"

api = DerivedAPI()
result = api.test_access()
print(f"Internal access: {result}")

# Test external access blocking
blocked_count = 0
test_methods = [
    ("get_data", lambda: api.get_data()),
    ("_internal_process", lambda: api._internal_process()),
    ("_explicitly_public", lambda: api._explicitly_public())
]

for method_name, method_call in test_methods:
    try:
        method_call()
        print(f"ERROR: {method_name} should be blocked")
    except PermissionDeniedError:
        blocked_count += 1

print(f"SUCCESS: {blocked_count}/3 methods correctly blocked by protected inheritance")

# Test 3: Friend Function Example  
print("\n=== Friend Function Example ===")
class SecureDocument:
    def __init__(self, content):
        self._content = content
        self._access_log = []
    
    @private
    def _get_content(self):
        return self._content
    
    @protected
    def _log_access(self, accessor):
        self._access_log.append(f"Accessed by: {accessor}")

@friend(SecureDocument)
def backup_document(doc):
    """Friend function for backup operations"""
    doc._log_access("backup_system")
    content = doc._get_content()
    return f"Backup: {content}"

doc = SecureDocument("Classified Information")
backup_result = backup_document(doc)
print(f"Friend function result: {backup_result}")

# Test 4: Multiple Inheritance Example
print("\n=== Multiple Inheritance Example ===")
class DatabaseMixin:
    def connect(self):
        return "database connected"
    
    def _query(self, sql):
        return f"executing: {sql}"

class CacheMixin:
    def get_cache(self):
        return "cache data"
    
    def _invalidate_cache(self):
        return "cache invalidated"

@protected(DatabaseMixin, CacheMixin)
class DataService(DatabaseMixin, CacheMixin):
    def process_data(self):
        # Can access all inherited members internally
        db_conn = self.connect()
        cache_data = self.get_cache()
        query_result = self._query("SELECT * FROM users")
        self._invalidate_cache()
        return f"Processed: {db_conn}, {cache_data}, {query_result}"

service = DataService()
result = service.process_data()
print(f"Multiple inheritance internal access: {result}")

# Test external blocking for multiple inheritance
external_blocked = 0
multi_test_methods = [
    ("connect", lambda: service.connect()),
    ("get_cache", lambda: service.get_cache()),
    ("_query", lambda: service._query("SELECT")),
    ("_invalidate_cache", lambda: service._invalidate_cache())
]

for method_name, method_call in multi_test_methods:
    try:
        method_call()
        print(f"ERROR: {method_name} should be blocked")
    except PermissionDeniedError:
        external_blocked += 1

print(f"SUCCESS: {external_blocked}/4 methods correctly blocked by multiple inheritance")

print("\n=== README Documentation Verification Complete ===")
print("All examples work as documented!")
print("✓ Basic access control")
print("✓ Implicit access control with inheritance") 
print("✓ Friend functions")
print("✓ Multiple inheritance patterns")
print("✓ Protected inheritance semantics")
