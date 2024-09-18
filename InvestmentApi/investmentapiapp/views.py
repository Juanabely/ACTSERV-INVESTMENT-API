from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import InvestmentAccount, Transaction, UserAccountPermission, CustomUser
from .serializers import (UserSerializer, InvestmentAccountSerializer, TransactionSerializer, 
                          AdminUserSerializer, UserAccountPermissionSerializer, CustomUserSerializer)
from .permissions import (CanViewInvestmentAccount, CanAddInvestmentAccount, 
                          CanChangeInvestmentAccount, CanDeleteInvestmentAccount, 
                          TransactionPermission, IsAdminUser)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]

class InvestmentAccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not CanViewInvestmentAccount().has_permission(request, self):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        accounts = InvestmentAccount.objects.all()
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
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, TransactionPermission]

    def get_queryset(self):
        user = self.request.user
        user_permissions = UserAccountPermission.objects.filter(user=user)
        allowed_accounts = user_permissions.exclude(permission='post').values_list('account', flat=True)
        return Transaction.objects.filter(account__in=allowed_accounts)

class UserAccountPermissionViewSet(viewsets.ModelViewSet):
    queryset = UserAccountPermission.objects.all()
    serializer_class = UserAccountPermissionSerializer
    permission_classes = [IsAdminUser]

class AdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

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