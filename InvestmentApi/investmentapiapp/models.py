# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class InvestmentAccount(models.Model):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class UserAccountPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_permissions')
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

class Transaction(models.Model):
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.account.name} - {self.amount} - {self.date}"

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
       