from rest_framework import permissions

class CanViewInvestmentAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('investmentapiapp.can_view_investment_account')

class CanAddInvestmentAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('investmentapiapp.can_add_investment_account')

class CanChangeInvestmentAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('investmentapiapp.can_change_investment_account')

class CanDeleteInvestmentAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('investmentapiapp.can_delete_investment_account')

class TransactionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.has_perm('investmentapiapp.can_add_transaction')
        elif view.action in ['list', 'retrieve']:
            return request.user.has_perm('investmentapiapp.can_view_transaction')
        elif view.action in ['update', 'partial_update']:
            return request.user.has_perm('investmentapiapp.can_change_transaction')
        elif view.action == 'destroy':
            return request.user.has_perm('investmentapiapp.can_delete_transaction')
        return False

class IsAdminUser(permissions.IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)