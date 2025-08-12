"""
Test friend methods functionality - methods of one class that are friends of another class
"""
import pytest

from limen import private, protected, public, friend
from limen.exceptions import PermissionDeniedError


@pytest.mark.friend_methods
@pytest.mark.cpp_semantics
class TestFriendMethods:
    """Test that friend methods work correctly with C++ semantics"""
    
    def test_private_friend_instance_method(self):
        """Test friend instance method accessing private members"""
        
        class SecretKeeper:
            @private
            def get_secret(self):
                return "top_secret"
        
        class TrustedFriend:
            @friend(SecretKeeper)
            def reveal_secret(self, keeper):
                return keeper.get_secret()
        
        class Stranger:
            def try_get_secret(self, keeper):
                return keeper.get_secret()
        
        # Friend method should have access
        keeper = SecretKeeper()
        friend_obj = TrustedFriend()
        assert friend_obj.reveal_secret(keeper) == "top_secret"
        
        # Non-friend should be blocked
        stranger = Stranger()
        with pytest.raises(PermissionDeniedError):
            stranger.try_get_secret(keeper)
        
        # Direct external access should be blocked
        with pytest.raises(PermissionDeniedError):
            keeper.get_secret()
    
    def test_protected_friend_instance_method(self):
        """Test friend instance method accessing protected members"""
        
        class SecretKeeper:
            @protected
            def get_protected_info(self):
                return "protected_info"
        
        class TrustedFriend:
            @friend(SecretKeeper)
            def get_info(self, keeper):
                return keeper.get_protected_info()
        
        class NonFriend:
            def try_get_info(self, keeper):
                return keeper.get_protected_info()
        
        # Friend method should have access
        keeper = SecretKeeper()
        friend_obj = TrustedFriend()
        assert friend_obj.get_info(keeper) == "protected_info"
        
        # Non-friend should be blocked
        non_friend = NonFriend()
        with pytest.raises(PermissionDeniedError):
            non_friend.try_get_info(keeper)
    
    def test_friend_classmethod(self):
        """Test friend class method accessing private members"""
        
        class SecretKeeper:
            @private
            def get_secret(self):
                return "class_secret"
        
        class TrustedFriend:
            @friend(SecretKeeper)
            @classmethod
            def reveal_secret_cls(cls, keeper):
                return keeper.get_secret()
        
        class NonFriend:
            @classmethod
            def try_get_secret(cls, keeper):
                return keeper.get_secret()
        
        # Friend class method should have access
        keeper = SecretKeeper()
        assert TrustedFriend.reveal_secret_cls(keeper) == "class_secret"
        
        # Non-friend class method should be blocked
        with pytest.raises(PermissionDeniedError):
            NonFriend.try_get_secret(keeper)
    
    def test_friend_staticmethod(self):
        """Test friend static method accessing private members"""
        
        class SecretKeeper:
            @private
            def get_secret(self):
                return "static_secret"
        
        class TrustedFriend:
            @friend(SecretKeeper)
            @staticmethod
            def reveal_secret_static(keeper):
                return keeper.get_secret()
        
        class NonFriend:
            @staticmethod
            def try_get_secret(keeper):
                return keeper.get_secret()
        
        # Friend static method should have access
        keeper = SecretKeeper()
        assert TrustedFriend.reveal_secret_static(keeper) == "static_secret"
        
        # Non-friend static method should be blocked
        with pytest.raises(PermissionDeniedError):
            NonFriend.try_get_secret(keeper)
    
    def test_multiple_friend_methods_same_class(self):
        """Test multiple friend methods in the same class"""
        
        class SecretKeeper:
            @private
            def get_secret1(self):
                return "secret1"
            
            @private
            def get_secret2(self):
                return "secret2"
        
        class TrustedFriend:
            @friend(SecretKeeper)
            def get_first_secret(self, keeper):
                return keeper.get_secret1()
            
            @friend(SecretKeeper)
            def get_second_secret(self, keeper):
                return keeper.get_secret2()
            
            def normal_method(self, keeper):
                # This should fail since it's not a friend method
                return keeper.get_secret1()
        
        keeper = SecretKeeper()
        friend_obj = TrustedFriend()
        
        # Both friend methods should work
        assert friend_obj.get_first_secret(keeper) == "secret1"
        assert friend_obj.get_second_secret(keeper) == "secret2"
        
        # Non-friend method should be blocked
        with pytest.raises(PermissionDeniedError):
            friend_obj.normal_method(keeper)
    
    def test_friend_method_with_access_control_decorators(self):
        """Test friend methods combined with access control decorators"""
        
        class SecretKeeper:
            @private
            def get_secret(self):
                return "combined_secret"
        
        class TrustedFriend:
            @private
            @friend(SecretKeeper)
            def private_friend_method(self, keeper):
                return f"private: {keeper.get_secret()}"
            
            @protected
            @friend(SecretKeeper)
            def protected_friend_method(self, keeper):
                return f"protected: {keeper.get_secret()}"
            
            @public
            @friend(SecretKeeper)
            def public_friend_method(self, keeper):
                return f"public: {keeper.get_secret()}"
            
            def internal_caller(self, keeper):
                # Internal access to friend methods
                return {
                    'private': self.private_friend_method(keeper),
                    'protected': self.protected_friend_method(keeper),
                    'public': self.public_friend_method(keeper)
                }
        
        class DerivedFriend(TrustedFriend):
            def try_access_friend_methods(self, keeper):
                results = {}
                
                # Try to access each friend method
                try:
                    results['private'] = self.private_friend_method(keeper)
                except PermissionDeniedError:
                    results['private'] = 'BLOCKED'
                
                try:
                    results['protected'] = self.protected_friend_method(keeper)
                except PermissionDeniedError:
                    results['protected'] = 'BLOCKED'
                
                try:
                    results['public'] = self.public_friend_method(keeper)
                except PermissionDeniedError:
                    results['public'] = 'BLOCKED'
                
                return results
        
        keeper = SecretKeeper()
        friend_obj = TrustedFriend()
        derived_obj = DerivedFriend()
        
        # Internal access should work for all
        internal_results = friend_obj.internal_caller(keeper)
        assert internal_results['private'] == 'private: combined_secret'
        assert internal_results['protected'] == 'protected: combined_secret'
        assert internal_results['public'] == 'public: combined_secret'
        
        # Derived class access
        derived_results = derived_obj.try_access_friend_methods(keeper)
        assert derived_results['private'] == 'BLOCKED'  # Private friend method blocked from derived
        assert derived_results['protected'] == 'protected: combined_secret'  # Protected accessible
        assert derived_results['public'] == 'public: combined_secret'  # Public accessible
        
        # External access to public friend method should work
        assert friend_obj.public_friend_method(keeper) == 'public: combined_secret'
        
        # External access to private/protected should be blocked
        with pytest.raises(PermissionDeniedError):
            friend_obj.private_friend_method(keeper)
        
        with pytest.raises(PermissionDeniedError):
            friend_obj.protected_friend_method(keeper)
    
    def test_friend_method_vs_friend_class(self):
        """Test that friend methods and friend classes work together"""
        
        class SecretKeeper:
            @private
            def get_secret(self):
                return "mixed_secret"
        
        @friend(SecretKeeper)  # Entire class is friend
        class FriendClass:
            def any_method_can_access(self, keeper):
                return keeper.get_secret()
        
        class PartialFriend:
            @friend(SecretKeeper)  # Only this method is friend
            def friend_method(self, keeper):
                return keeper.get_secret()
            
            def non_friend_method(self, keeper):
                return keeper.get_secret()
        
        keeper = SecretKeeper()
        
        # Friend class - any method can access
        friend_class_obj = FriendClass()
        assert friend_class_obj.any_method_can_access(keeper) == "mixed_secret"
        
        # Partial friend - only designated method can access
        partial_friend_obj = PartialFriend()
        assert partial_friend_obj.friend_method(keeper) == "mixed_secret"
        
        with pytest.raises(PermissionDeniedError):
            partial_friend_obj.non_friend_method(keeper)
    
    def test_friend_methods_with_inheritance(self):
        """Test friend methods with class inheritance"""
        
        class BaseSecret:
            @private
            def base_secret(self):
                return "base_secret"
        
        class DerivedSecret(BaseSecret):
            @private  
            def derived_secret(self):
                return "derived_secret"
        
        class FriendOfBase:
            @friend(BaseSecret)
            def access_base_secret(self, obj):
                return obj.base_secret()
        
        class FriendOfDerived:
            @friend(DerivedSecret)
            def access_derived_secret(self, obj):
                return obj.derived_secret()
        
        base_obj = BaseSecret()
        derived_obj = DerivedSecret()
        friend_base = FriendOfBase()
        friend_derived = FriendOfDerived()
        
        # Friend of base can access base secret on both objects
        assert friend_base.access_base_secret(base_obj) == "base_secret"
        assert friend_base.access_base_secret(derived_obj) == "base_secret"
        
        # Friend of derived can access derived secret
        assert friend_derived.access_derived_secret(derived_obj) == "derived_secret"
        
        # But not the other way around
        with pytest.raises(AttributeError):
            friend_derived.access_derived_secret(base_obj)  # base_obj doesn't have derived_secret
    
    def test_friend_method_order_with_decorators(self):
        """Test that decorator order works correctly with friend methods"""
        
        class SecretKeeper:
            @private
            def get_secret(self):
                return "order_secret"
        
        class TrustedFriend:
            # Test different orders
            @friend(SecretKeeper)
            @classmethod
            def friend_then_classmethod(cls, keeper):
                return f"friend_then_cls: {keeper.get_secret()}"
            
            @classmethod
            @friend(SecretKeeper) 
            def classmethod_then_friend(cls, keeper):
                return f"cls_then_friend: {keeper.get_secret()}"
            
            @friend(SecretKeeper)
            @staticmethod
            def friend_then_staticmethod(keeper):
                return f"friend_then_static: {keeper.get_secret()}"
            
            @staticmethod
            @friend(SecretKeeper)
            def staticmethod_then_friend(keeper):
                return f"static_then_friend: {keeper.get_secret()}"
        
        keeper = SecretKeeper()
        
        # All combinations should work
        assert TrustedFriend.friend_then_classmethod(keeper) == "friend_then_cls: order_secret"
        assert TrustedFriend.classmethod_then_friend(keeper) == "cls_then_friend: order_secret"
        assert TrustedFriend.friend_then_staticmethod(keeper) == "friend_then_static: order_secret"
        assert TrustedFriend.staticmethod_then_friend(keeper) == "static_then_friend: order_secret"
