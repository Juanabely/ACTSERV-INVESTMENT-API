# accounts/permissions.py
from rest_framework import permissions
from .models import UserAccountPermission

class InvestmentAccountPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            user_permission = UserAccountPermission.objects.get(user=request.user, account=obj)
        except UserAccountPermission.DoesNotExist:
            return False

        if user_permission.permission == 'view':
            return request.method in permissions.SAFE_METHODS
        elif user_permission.permission == 'crud':
            return True
        elif user_permission.permission == 'post':
            return request.method == 'POST'
        
        return False

class TransactionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # This method is called for list and create actions
        if view.action == 'create':
            # For create, we need to check if the user has 'post' or higher permissions on the specified account
            account_id = request.data.get('account')
            if not account_id:
                return False
            try:
                user_permission = UserAccountPermission.objects.get(user=request.user, account_id=account_id)
                return user_permission.permission in ['post', 'crud', 'admin']
            except UserAccountPermission.DoesNotExist:
                return False
        elif view.action == 'list':
            # For list, we allow access if the user has any account permissions
            # The filtering is done in the get_queryset method
            return UserAccountPermission.objects.filter(user=request.user).exists()
        return True  # Allow other actions to pass through to has_object_permission

    def has_object_permission(self, request, view, obj):
        # This method is called for retrieve, update, partial_update, destroy actions
        try:
            user_permission = UserAccountPermission.objects.get(user=request.user, account=obj.account)
        except UserAccountPermission.DoesNotExist:
            return False

        if user_permission.permission == 'view':
            return request.method in permissions.SAFE_METHODS
        elif user_permission.permission in ['crud', 'admin']:
            return True
        elif user_permission.permission == 'post':
            return False  # 'post' permission doesn't allow viewing or modifying existing transactions
        
        return False