from rest_framework import serializers
from django.contrib.auth.models import User
from .models import InvestmentAccount, UserAccountPermission, Transaction, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserAccountPermissionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)

    class Meta:
        model = UserAccountPermission
        fields = ['username', 'account', 'permission']

    def create(self, validated_data):
        username = validated_data.pop('username')
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"username": "User does not exist."})
        
        validated_data['user'] = user
        return super().create(validated_data)

class UserPermissionSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')

    class Meta:
        model = UserAccountPermission
        fields = ['user_id', 'username', 'permission']

class InvestmentAccountSerializer(serializers.ModelSerializer):
    users = UserPermissionSerializer(source='user_permissions', many=True, read_only=True)

    class Meta:
        model = InvestmentAccount
        fields = ['id', 'name', 'balance', 'users']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('request').user
        if not user.is_staff and not user.is_superuser:
            representation.pop('users', None)
        return representation

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'amount', 'date', 'description']

    def validate(self, data):
        user = self.context['request'].user
        account = data['account']
        try:
            permission = UserAccountPermission.objects.get(user=user, account=account)
            if permission.permission not in ['crud', 'post']:
                raise serializers.ValidationError("You don't have permission to create transactions for this account.")
        except UserAccountPermission.DoesNotExist:
            raise serializers.ValidationError("You don't have permission for this account.")
        return data

class AdminTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'amount', 'date', 'description']

class AdminUserSerializer(serializers.ModelSerializer):
    transactions = serializers.SerializerMethodField()
    total_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'transactions', 'total_balance']

    def get_transactions(self, obj):
        account_ids = obj.account_permissions.values_list('account_id', flat=True)
        transactions = Transaction.objects.filter(account_id__in=account_ids)
        if transactions.exists():
            return AdminTransactionSerializer(transactions, many=True).data
        else:
            return []  