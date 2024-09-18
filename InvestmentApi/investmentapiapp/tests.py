from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from .models import InvestmentAccount, UserAccountPermission, Transaction, CustomUser

User = CustomUser
class TransactionPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345', email='jQsQ8@example.com')
        self.admin_user = User.objects.create_user(username='adminuser', password='12345', email='admin8@example.com', is_staff=True, is_superuser=True)
        self.account = InvestmentAccount.objects.create(name='Test Account', balance=1000.00)
        
    def test_view_permission(self):
        UserAccountPermission.objects.create(user=self.user, account=self.account, permission='view')
        self.client.force_authenticate(user=self.user)
        Transaction.objects.create(account=self.account, amount=100, description='Test')
        response = self.client.get('/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_permission(self):
        UserAccountPermission.objects.create(user=self.user, account=self.account, permission='post')
        self.client.force_authenticate(user=self.user)
        data = {'account': self.account.id, 'amount': 100, 'description': 'Test Transaction'}
        response = self.client.post('/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Ensure user with only 'post' permission can't view transactions
        response = self.client.get('/transactions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        

    def test_crud_permission(self):
        UserAccountPermission.objects.create(user=self.user, account=self.account, permission='crud')
        self.client.force_authenticate(user=self.user)
        
        # Create
        data = {'account': self.account.id, 'amount': 100, 'description': 'Test Transaction'}
        response = self.client.post('/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        transaction_id = response.data['id']
        
        # Read
        response = self.client.get(f'/transactions/{transaction_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        response = self.client.put(f'/transactions/{transaction_id}/', {'account': self.account.id, 'amount': 200, 'description': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(f'/transactions/{transaction_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_permissions(self):
        self.client.force_authenticate(user=self.admin_user)
        
        # Test creating a new user
        response = self.client.post('/customusers/', {'username': 'newuser', 'password': 'newpassword', 'email': 'gqkK7@example.com'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test creating a new account
        response = self.client.post('/accounts/', {'name': 'New Account', 'balance': 2000.00})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_account_id = response.data['id']
        
        # Test giving permissions
        response = self.client.post('/permissions/', {'username': self.user.username, 'account': new_account_id, 'permission': 'view'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_admin_cant_perform_admin_actions(self):
        self.client.force_authenticate(user=self.user)
        
        # Try to create a new user
        response = self.client.post('/customusers/', {'username': 'newuser', 'password': 'newpassword', 'email': 'gqkKold7@example.com'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to create a new account
        response = self.client.post('/accounts/', {'name': 'New Account', 'balance': 2000.00})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to give permissions
        response = self.client.post('/permissions/', {'user': self.user.id, 'account': self.account.id, 'permission': 'view'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)