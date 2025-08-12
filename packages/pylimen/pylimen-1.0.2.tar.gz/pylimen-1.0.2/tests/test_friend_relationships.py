"""
Test friend relationships and access control
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from limen import private, protected, public, friend
from limen.exceptions import PermissionDeniedError
from limen.system.access_control import get_access_control_system

@pytest.mark.cpp_semantics
@pytest.mark.access_control
class TestFriendRelationships:
    """Test C++ style friend relationships"""
    
    def test_friend_class_private_access(self):
        """Test that friend classes can access private members"""
        class Target:
            @private
            def private_method(self):
                return "target_private_method"
            
            @private
            @staticmethod
            def private_static():
                return "target_private_static"
            
            @private
            @classmethod
            def private_class(cls):
                return f"target_private_class_{cls.__name__}"
            
            @private
            @property
            def private_prop(self):
                return "target_private_prop"
        
        @friend(Target)
        class FriendClass:
            def access_target_private(self, target_obj):
                return {
                    'private_method': target_obj.private_method(),
                    'private_static': target_obj.private_static(),
                    'private_class': target_obj.private_class(),
                    'private_prop': target_obj.private_prop
                }
        
        class NonFriend:
            def try_access_target_private(self, target_obj):
                results = {}
                try:
                    results['private_method'] = target_obj.private_method()
                except PermissionDeniedError:
                    results['private_method'] = 'BLOCKED'
                
                try:
                    results['private_static'] = target_obj.private_static()
                except PermissionDeniedError:
                    results['private_static'] = 'BLOCKED'
                
                try:
                    results['private_class'] = target_obj.private_class()
                except PermissionDeniedError:
                    results['private_class'] = 'BLOCKED'
                
                try:
                    results['private_prop'] = target_obj.private_prop
                except PermissionDeniedError:
                    results['private_prop'] = 'BLOCKED'
                
                return results
        
        # Test friend access
        target = Target()
        friend_obj = FriendClass()
        non_friend = NonFriend()
        
        # Friend should have access
        friend_results = friend_obj.access_target_private(target)
        assert friend_results['private_method'] == "target_private_method"
        assert friend_results['private_static'] == "target_private_static"
        assert friend_results['private_class'] == "target_private_class_Target"
        assert friend_results['private_prop'] == "target_private_prop"
        
        # Non-friend should be blocked
        non_friend_results = non_friend.try_access_target_private(target)
        assert non_friend_results['private_method'] == 'BLOCKED'
        assert non_friend_results['private_static'] == 'BLOCKED'
        assert non_friend_results['private_class'] == 'BLOCKED'
        assert non_friend_results['private_prop'] == 'BLOCKED'
    
    def test_friend_class_protected_access(self):
        """Test that friend classes can access protected members"""
        class Target:
            @protected
            def protected_method(self):
                return "target_protected_method"
            
            @protected
            @property
            def protected_prop(self):
                return "target_protected_prop"
        
        @friend(Target)
        class FriendClass:
            def access_target_protected(self, target_obj):
                return {
                    'protected_method': target_obj.protected_method(),
                    'protected_prop': target_obj.protected_prop
                }
        
        class NonFriend:
            def try_access_target_protected(self, target_obj):
                results = {}
                try:
                    results['protected_method'] = target_obj.protected_method()
                except PermissionDeniedError:
                    results['protected_method'] = 'BLOCKED'
                
                try:
                    results['protected_prop'] = target_obj.protected_prop
                except PermissionDeniedError:
                    results['protected_prop'] = 'BLOCKED'
                
                return results
        
        # Test friend access
        target = Target()
        friend_obj = FriendClass()
        non_friend = NonFriend()
        
        # Friend should have access
        friend_results = friend_obj.access_target_protected(target)
        assert friend_results['protected_method'] == "target_protected_method"
        assert friend_results['protected_prop'] == "target_protected_prop"
        
        # Non-friend should be blocked
        non_friend_results = non_friend.try_access_target_protected(target)
        assert non_friend_results['protected_method'] == 'BLOCKED'
        assert non_friend_results['protected_prop'] == 'BLOCKED'


@pytest.mark.cpp_semantics
@pytest.mark.access_control
class TestMultipleFriendships:
    """Test multiple friend relationships"""
    
    def test_multiple_friends_same_target(self):
        """Test that multiple classes can be friends of the same target"""
        class Target:
            @private
            def private_method(self):
                return "target_private"
        
        @friend(Target)
        class Friend1:
            def access_target(self, target_obj):
                return target_obj.private_method()
        
        @friend(Target)
        class Friend2:
            def access_target(self, target_obj):
                return target_obj.private_method()
        
        target = Target()
        friend1 = Friend1()
        friend2 = Friend2()
        
        # Both friends should have access
        assert friend1.access_target(target) == "target_private"
        assert friend2.access_target(target) == "target_private"
    
    def test_friendship_not_symmetric(self):
        """Test that friendship is not symmetric by default"""
        class Target:
            @private
            def secret_data(self):
                return "secret"
        
        @friend(Target)
        class FriendClass:
            def access_target_private(self, target_obj):
                return target_obj.secret_data()
        
        # Friend can access target's private members
        friend_obj = FriendClass()
        target_obj = Target()
        assert friend_obj.access_target_private(target_obj) == "secret"
        
        # But target cannot access friend's private members (friendship is not symmetric)
        # Test that the friendship is registered correctly
        system = get_access_control_system()
        assert system.is_friend(Target, FriendClass)
        assert not system.is_friend(FriendClass, Target)

    def test_mutual_friend_relationships(self):
        """Test mutual friend relationships between classes"""
        class ClassA:
            @private
            def private_method_a(self):
                return "private_a"
            
            def access_friend_b(self, b_obj):
                return b_obj.private_method_b()
        
        class ClassB:
            @private
            def private_method_b(self):
                return "private_b"
            
            def access_friend_a(self, a_obj):
                return a_obj.private_method_a()
        
        # Make them mutual friends
        friend(ClassA)(ClassB)
        friend(ClassB)(ClassA)
        
        a_obj = ClassA()
        b_obj = ClassB()
        
        # Both should be able to access each other's private members
        assert b_obj.access_friend_a(a_obj) == "private_a"
        assert a_obj.access_friend_b(b_obj) == "private_b"
    
    def test_friend_inheritance_access(self):
        """Test friend access with inheritance hierarchies"""
        class Base:
            @private
            def base_private(self):
                return "base_private"
            
            @protected
            def base_protected(self):
                return "base_protected"
        
        class Derived(Base):
            pass
        
        @friend(Base)
        class FriendOfBase:
            def access_base_members(self, obj):
                return {
                    'base_private': obj.base_private(),
                    'base_protected': obj.base_protected()
                }
        
        # Friend should be able to access both base and derived objects
        friend_obj = FriendOfBase()
        base_obj = Base()
        derived_obj = Derived()
        
        # Access to base object
        base_results = friend_obj.access_base_members(base_obj)
        assert base_results['base_private'] == "base_private"
        assert base_results['base_protected'] == "base_protected"
        
        # Access to derived object should also work
        derived_results = friend_obj.access_base_members(derived_obj)
        assert derived_results['base_private'] == "base_private"
        assert derived_results['base_protected'] == "base_protected"
