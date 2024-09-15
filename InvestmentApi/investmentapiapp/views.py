# accounts/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import InvestmentAccount, Transaction, UserAccountPermission
from .serializers import (UserSerializer, InvestmentAccountSerializer, TransactionSerializer, 
                          AdminUserSerializer, UserAccountPermissionSerializer)
from .permissions import InvestmentAccountPermission, TransactionPermission

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class InvestmentAccountViewSet(viewsets.ModelViewSet):
    queryset = InvestmentAccount.objects.all()
    serializer_class = InvestmentAccountSerializer
    permission_classes = [permissions.IsAuthenticated, InvestmentAccountPermission, permissions.IsAdminUser]

    def get_queryset(self):
        return InvestmentAccount.objects.filter(user_permissions__user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, TransactionPermission]

    def get_queryset(self):
        user = self.request.user
        user_permissions = UserAccountPermission.objects.filter(user=user)
        
        # Users with 'post' permission should not see any transactions
        if user_permissions.filter(permission='post').exists() and not user_permissions.exclude(permission='post').exists():
            return Transaction.objects.none()
        
        # For users with 'view', 'crud', or 'admin' permissions, show transactions for their accounts
        allowed_accounts = user_permissions.exclude(permission='post').values_list('account', flat=True)
        return Transaction.objects.filter(account__in=allowed_accounts)

    def perform_create(self, serializer):
        account = serializer.validated_data.get('account')
        user_permission = UserAccountPermission.objects.filter(user=self.request.user, account=account).first()
        
        if user_permission and user_permission.permission in ['post', 'crud', 'admin']:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You don't have permission to create transactions for this account.")

# accounts/views.py

class UserAccountPermissionViewSet(viewsets.ModelViewSet):
    queryset = UserAccountPermission.objects.all()
    serializer_class = UserAccountPermissionSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['get'])
    def user_transactions(self, request, pk=None):
        user = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        account_ids = user.account_permissions.values_list('account_id', flat=True)
        transactions = Transaction.objects.filter(account_id__in=account_ids)

        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)

        total_balance = transactions.aggregate(Sum('amount'))['amount__sum'] or 0

        serializer = self.get_serializer({
            'id': user.id,
            'username': user.username,
            'transactions': transactions,
            'total_balance': total_balance
        })
        return Response(serializer.data)