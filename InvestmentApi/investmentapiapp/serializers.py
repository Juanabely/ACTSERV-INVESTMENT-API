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
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# accounts/serializers.py

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

class InvestmentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentAccount
        fields = ['id', 'name', 'balance']  

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('request').user
        if user.is_staff:  # Only show user_permissions to staff users
            user_permissions = UserAccountPermission.objects.filter(account=instance)
            representation['user_permissions'] = UserAccountPermissionSerializer(user_permissions, many=True).data
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
        model = User
        fields = ['id', 'username', 'transactions', 'total_balance']

    def get_transactions(self, obj):
        account_ids = obj.account_permissions.values_list('account_id', flat=True)
        transactions = Transaction.objects.filter(account_id__in=account_ids)
        return AdminTransactionSerializer(transactions, many=True).data