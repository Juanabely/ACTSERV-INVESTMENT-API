from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import InvestmentAccount, Transaction, UserAccountPermission, CustomUser
from .serializers import (InvestmentAccountSerializer, TransactionSerializer, 
                          AdminUserSerializer, UserAccountPermissionSerializer, CustomUserSerializer)
from .permissions import (CanViewInvestmentAccount, CanAddInvestmentAccount, 
                          CanChangeInvestmentAccount, CanDeleteInvestmentAccount, 
                          TransactionPermission, IsAdminUser)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class CustomUserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    This is the user model viewset.Can only be accessed by admins.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]

class InvestmentAccountListView(APIView):
    """
    This viewset provides `list` and `create` actions for the `InvestmentAccount` model.
    Can only be accessed by authenticated users.
    Can only be accessed by admins & manager roles
    """

    permission_classes = [IsAuthenticated]
    def get(self, request):
        accounts = InvestmentAccount.objects.prefetch_related('user_permissions__user').all()
        serializer = InvestmentAccountSerializer(accounts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not CanAddInvestmentAccount().has_permission(request, self):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = InvestmentAccountSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvestmentAccountDetailView(APIView):
    """
    This viewset provides `list`, `retrieve`, `update` and `destroy` actions for the `InvestmentAccount` model.
    Can only be accessed by authenticated users.
    Can only be accessed by admins & manager roles
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, account_id):
        try:
            return InvestmentAccount.objects.get(id=account_id)
        except InvestmentAccount.DoesNotExist:
            return None

    def get(self, request, account_id):
        if not CanViewInvestmentAccount().has_permission(request, self):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        account = self.get_object(account_id)
        if account is None:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InvestmentAccountSerializer(account, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, account_id):
        if not CanChangeInvestmentAccount().has_permission(request, self):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        account = self.get_object(account_id)
        if account is None:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InvestmentAccountSerializer(account, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, account_id):
        if not CanDeleteInvestmentAccount().has_permission(request, self):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        account = self.get_object(account_id)
        if account is None:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TransactionViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    Can only be accessed by authenticated users.
    Can only be accessed by members that belong to an investment accounts that the user has permission to.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, TransactionPermission]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # for schema generation
            return Transaction.objects.none()
        user = self.request.user
        if user.is_authenticated:
            user_permissions = UserAccountPermission.objects.filter(user=user)
            allowed_accounts = user_permissions.exclude(permission='post').values_list('account', flat=True)
            return Transaction.objects.filter(account__in=allowed_accounts)
        return Transaction.objects.none()

class CanAssignAccountPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('investmentapiapp.can_add_investment_account')
        )

class UserAccountPermissionViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    Can be accessed by admins and users with 'can_add_investment_account' permission.
    This viewset is for the user account permission model which links a user to an investment account 
    and the permissions they have in that account.
    """
    queryset = UserAccountPermission.objects.all()
    serializer_class = UserAccountPermissionSerializer
    permission_classes = [CanAssignAccountPermission]

    def perform_create(self, serializer):
        if not self.request.user.is_staff and self.request.user != serializer.validated_data['user']:
            raise PermissionDenied("You can only assign permissions to yourself.")
        serializer.save()

    def perform_update(self, serializer):
        if not self.request.user.is_staff and self.request.user != serializer.instance.user:
            raise PermissionDenied("You can only update your own permissions.")
        serializer.save()

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserAccountPermission.objects.all()
        return UserAccountPermission.objects.filter(user=self.request.user)

class AdminViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    Can only be accessed by admins.
    This viewset allows admins to filter start and end date for transactions.
    """
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['get'])
    def user_transactions(self, request, pk=None):
        user = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        account_ids = CustomUser.account_permissions.values_list('account_id', flat=True)
        transactions = Transaction.objects.filter(account_id__in=account_ids)

        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)

        total_balance = transactions.aggregate(Sum('amount'))['amount__sum'] or 0

        transaction_serializer = TransactionSerializer(transactions, many=True)
        serializer = self.get_serializer({
            'id': user.id,
            'username': user.username,
            'transactions': transaction_serializer.data,
            'total_balance': total_balance
        })
        return Response(serializer.data)