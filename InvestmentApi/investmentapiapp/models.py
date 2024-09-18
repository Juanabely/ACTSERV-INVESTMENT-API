from django.db import models
from django.contrib.auth.models import  Group, Permission, AbstractBaseUser, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from .manager import CustomUserManager
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('investor', 'Investor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='investor')
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    def __str__(self):
        return self.username
@receiver(post_save, sender=CustomUser)
def create_user_group(sender, instance=None, created=False, **kwargs):
    if created:
        group_name = f'{instance.role}s'
        group, _ = Group.objects.get_or_create(name=group_name)
        
        permission_map = {
            'admin': ['can_view_investment_account', 'can_add_investment_account', 'can_change_investment_account', 'can_delete_investment_account'],
            'manager': ['can_view_investment_account', 'can_add_investment_account'],
            'investor': ['can_view_investment_account']
        }
        
        content_type = ContentType.objects.get_for_model(InvestmentAccount)
        
        for permission_name in permission_map[instance.role]:
            permission, _ = Permission.objects.get_or_create(
                codename=permission_name,
                content_type=content_type,
                defaults={'name': permission_name}
            )
            group.permissions.add(permission)
        
        instance.groups.add(group)       

class InvestmentAccount(models.Model):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        permissions= [
            ('can_view_investment_account', 'Can view investment account'),
            ('can_add_investment_account', 'Can add investment account'),
            ('can_change_investment_account', 'Can change investment account'),
            ('can_delete_investment_account', 'Can delete investment account'),
        ]
    def __str__(self):
        return self.name

class UserAccountPermission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='account_permissions')
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE, related_name='user_permissions', default=None)
    
    VIEW = 'view'
    CRUD = 'crud'
    POST = 'post'
    PERMISSION_CHOICES = [
        (VIEW, 'View Only'),
        (CRUD, 'Full CRUD'),
        (POST, 'Post Only'),
    ]
    permission = models.CharField(max_length=4, choices=PERMISSION_CHOICES)

    class Meta:
        unique_together = ['user', 'account']

    def __str__(self):
        return f"{self.user.username} - {self.account.name} - {self.permission}"
@receiver(post_save, sender=UserAccountPermission)
def create_group(sender, instance=None, created=False, **kwargs):
    if created:
        group_name = f"{instance.account.name}_{instance.permission}"
        group, created = Group.objects.get_or_create(name=group_name)

        instance.user.groups.add(group)

        permission_map = {
            'view': ['can_view_transaction'],
            'crud': ['can_view_transaction', 'can_change_transaction', 'can_add_transaction', 'can_delete_transaction'],
            'post': ['can_add_transaction']
        }

        transaction_content_type = ContentType.objects.get_for_model(Transaction)

        for permission_name in permission_map[instance.permission]:
            permission, created = Permission.objects.get_or_create(
                codename=permission_name,
                content_type=transaction_content_type,
                defaults={'name': permission_name}
            )
            group.permissions.add(permission)     
class Transaction(models.Model):
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)
    
    class Meta:
        permissions = [
            ('can_view_transaction', 'Can view transaction'),
            ('can_add_transaction', 'Can add transaction'),
            ('can_change_transaction', 'Can change transaction'),
            ('can_delete_transaction', 'Can delete transaction'),
        ]
    def __str__(self):
        return f"{self.account.name} - {self.amount} - {self.date}"

@receiver(post_save, sender=CustomUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
       