from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    
    TransactionViewSet,
    UserAccountPermissionViewSet,
    AdminViewSet,
    CustomUserViewSet,
    InvestmentAccountListView,
    InvestmentAccountDetailView,
)

router = routers.SimpleRouter()
router.register(r'customusers', CustomUserViewSet, basename='customusers')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'permissions', UserAccountPermissionViewSet, basename='permissions')
router.register(r'admins', AdminViewSet, basename='admins')

urlpatterns = [
    path('', include(router.urls)),
   
    path('accounts/', InvestmentAccountListView.as_view()),
    path('accounts/<int:account_id>/', InvestmentAccountDetailView.as_view()),
]