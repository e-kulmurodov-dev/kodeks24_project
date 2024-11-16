from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from apps.views import (
    CategoryListCreateAPIView,
    ProductListCreateAPIView,
    RegisterCreateAPIView,
    UserListAPIView,
)

urlpatterns = [
    path('users', UserListAPIView.as_view(), name='users'),
    path('categories', CategoryListCreateAPIView.as_view(), name='category-list'),
    path('products-postgres', ProductListCreateAPIView.as_view(), name='product-list'),
    path('auth/register', RegisterCreateAPIView.as_view(), name='register'),
    path('token', obtain_auth_token, name='token_obtain_pair'),
]