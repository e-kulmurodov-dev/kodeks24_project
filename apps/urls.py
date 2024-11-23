from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from apps.views import (
    CategoryListCreateAPIView,
    ProductListCreateAPIView,
    RegisterCreateAPIView,
    UserListAPIView, WishlistCreateAPIView, CartListCreateAPIView, LoginCreateAPIView, ActivateUserAPIView,
    ProductRetrieveAPIView,
)

urlpatterns = [
    path('categories', CategoryListCreateAPIView.as_view(), name='category-list'),
    path('products', ProductListCreateAPIView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductRetrieveAPIView.as_view(), name='product-detail-by-slug'),
    path('users', UserListAPIView.as_view(), name='users'),

    path('wishlist', WishlistCreateAPIView.as_view(), name='wishlist'),
    path('cart', CartListCreateAPIView.as_view(), name='cart'),

    path('register', RegisterCreateAPIView.as_view(), name='register'),
    path('login', LoginCreateAPIView.as_view(), name='login'),
    path('activate-user', ActivateUserAPIView.as_view(), name='activate-user'),

    path('token', obtain_auth_token, name='token_obtain_pair'),
]

