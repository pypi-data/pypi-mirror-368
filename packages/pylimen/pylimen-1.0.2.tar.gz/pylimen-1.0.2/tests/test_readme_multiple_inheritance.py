#!/usr/bin/env python3
"""Test the complex multiple inheritance examples from the README."""

from limen import protected, private
from limen.exceptions import PermissionDeniedError

def test_qux_multiple_inheritance():
    """Test the @protected(Foo, Bar) class Qux example."""
    
    class Foo:
        def foo_public(self):              # Implicit @public
            return "foo public method"
        
        def _foo_protected(self):          # Implicit @protected
            return "foo protected method"
        
        def __foo_private(self):           # Implicit @private
            return "foo private method"

    class Bar:
        def bar_public(self):              # Implicit @public
            return "bar public method"
        
        def _bar_protected(self):          # Implicit @protected
            return "bar protected method"
        
        @private                           # Explicit @private
        def bar_explicit_private(self):
            return "bar explicit private"

    # Multiple inheritance with access control applied to all base classes
    @protected(Foo, Bar)
    class Qux(Foo, Bar):
        def qux_operation(self):
            # Can access all inherited members internally
            foo_pub = self.foo_public()              # Protected due to inheritance
            foo_prot = self._foo_protected()         # Protected (unchanged)
            bar_pub = self.bar_public()              # Protected due to inheritance
            bar_prot = self._bar_protected()         # Protected (unchanged)
            
            return f"Qux: {foo_pub}, {foo_prot}, {bar_pub}, {bar_prot}"

    qux = Qux()
    result = qux.qux_operation()          # Works internally
    
    # Verify it works
    assert "foo public method" in result
    assert "foo protected method" in result
    assert "bar public method" in result
    assert "bar protected method" in result
    
    # External access should be blocked
    try:
        qux.foo_public()
        assert False, "Should have raised PermissionDeniedError"
    except PermissionDeniedError:
        pass  # Expected
    
    try:
        qux.bar_public()
        assert False, "Should have raised PermissionDeniedError"
    except PermissionDeniedError:
        pass  # Expected

def test_advanced_data_service():
    """Test the complex triple inheritance example."""
    
    class DatabaseMixin:
        def connect(self):                   # Implicit @public
            return "database connected"
        
        def _query(self, sql):              # Implicit @protected
            return f"executing: {sql}"
        
        def __validate_connection(self):     # Implicit @private
            return "connection valid"

    class CacheMixin:
        def get_cache(self):                # Implicit @public
            return "cache data"
        
        def _invalidate_cache(self):        # Implicit @protected
            return "cache invalidated"
        
        @private                            # Explicit @private
        def _clear_all_cache(self):
            return "all cache cleared"

    class LoggingMixin:
        def log_info(self, message):        # Implicit @public
            return f"INFO: {message}"
        
        def _log_debug(self, message):      # Implicit @protected
            return f"DEBUG: {message}"

    # Triple inheritance with different access patterns
    @protected(DatabaseMixin, CacheMixin)   # Protected inheritance for DB and Cache
    @private(LoggingMixin)                  # Private inheritance for Logging
    class AdvancedDataService(DatabaseMixin, CacheMixin, LoggingMixin):
        def comprehensive_operation(self):
            # Database methods - protected due to inheritance
            db_conn = self.connect()                      # Protected
            query_result = self._query("SELECT * FROM")   # Protected
            
            # Cache methods - protected due to inheritance  
            cache_data = self.get_cache()                 # Protected
            self._invalidate_cache()                      # Protected
            
            # Logging methods - private due to inheritance
            info_log = self.log_info("Processing data")   # Private
            debug_log = self._log_debug("Cache accessed") # Private
            
            return {
                'database': f"{db_conn}, {query_result}",
                'cache': f"{cache_data}",
                'logging': f"{info_log}, {debug_log}"
            }
        
        def public_interface(self):
            # Expose controlled functionality
            return self.comprehensive_operation()

    service = AdvancedDataService()
    result = service.public_interface()   # Works - controlled access
    
    # Verify the result
    assert 'database' in result
    assert 'cache' in result
    assert 'logging' in result
    assert 'database connected' in result['database']
    assert 'cache data' in result['cache']
    
    # External access should be completely blocked
    try:
        service.connect()
        assert False, "Should have raised PermissionDeniedError"
    except PermissionDeniedError:
        pass  # Expected
        
    try:
        service.get_cache()
        assert False, "Should have raised PermissionDeniedError"  
    except PermissionDeniedError:
        pass  # Expected
        
    try:
        service.log_info("test")
        assert False, "Should have raised PermissionDeniedError"
    except PermissionDeniedError:
        pass  # Expected

if __name__ == "__main__":
    test_qux_multiple_inheritance()
    test_advanced_data_service()
    print("All multiple inheritance examples work correctly!")
