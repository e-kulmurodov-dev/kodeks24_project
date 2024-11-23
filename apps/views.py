import random

from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.models import CustomUser, Category, Product, Wishlist, Cart
from apps.pagination import CustomPagination
from apps.serializers import UserModelSerializer, CategoryModelSerializer, ProductModelSerializer, \
    RegisterUserModelSerializer, WishlistModelSerializer, CartModelSerializer, ActivateUserModelSerializer, \
    LoginModelSerializer, ProductDetailSerializer
from apps.tasks import send_confirmation_code


@extend_schema(tags=['product'])
class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryModelSerializer
    pagination_class = CustomPagination



@extend_schema(tags=['product'])
class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductModelSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'quantity', 'category__name']
    ordering = ['price']
    filterset_fields = ['category', 'owner']
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

@extend_schema(tags=['product'])
class ProductRetrieveAPIView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    permission_classes = AllowAny,


@extend_schema(tags=['auth'])
class RegisterCreateAPIView(APIView):
    serializer_class = RegisterUserModelSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = RegisterUserModelSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            confirmation_code = random.randint(100000, 600000)
            print(f"Raw password: {password}")
            OTP_EXPIRY_TIME = 120  # 2 minutes
            cache.set(email, {"username": username, "password": password, "confirmation_code": confirmation_code},
                      OTP_EXPIRY_TIME)

            message = f"Thanks for registering! Please confirm your account with this code: {confirmation_code}"
            send_confirmation_code.delay(email, message)

            return Response({"message": "Confirmation code sent to your email."}, status=201)

        return Response(serializer.errors, status=400)


@extend_schema(tags=['auth'])
class ActivateUserAPIView(APIView):
    serializer_class = ActivateUserModelSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        confirmation_code = request.data.get("confirmation_code")

        cached_data = cache.get(email)

        if not cached_data:
            return Response({"error": "Confirmation code expired or invalid."}, status=400)

        if str(cached_data["confirmation_code"]) != str(confirmation_code):
            return Response({"error": "Invalid confirmation code."}, status=400)

        print(cached_data['password'])
        user = CustomUser.objects.create_user(
            username=cached_data["username"],
            password=cached_data['password'],
            email=email,
            is_active=True
        )

        cache.delete(email)
        return Response({"message": "Account successfully activated."}, status=200)


@extend_schema(tags=['auth'])
class LoginCreateAPIView(APIView):
    serializer_class = LoginModelSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email_or_username = request.data.get("email_or_username")
        password = request.data.get("password")

        user = CustomUser.objects.filter(
            Q(email=email_or_username) | Q(username=email_or_username)
        ).first()

        print(f"Stored hash: {user.password}")
        print(f"Password match: {user.check_password(password)}")

        if not user.is_active:
            return Response({"error": "Account is not activated."}, status=403)

        if not user or not user.check_password(password):
            return Response({"error": "Invalid credentials."}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=200)


class UserListAPIView(ListCreateAPIView):
    queryset = CustomUser.objects.order_by('id')
    serializer_class = UserModelSerializer
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema(tags=['user'])
class WishlistCreateAPIView(ListCreateAPIView):
    serializer_class = WishlistModelSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        product_id = serializer.validated_data['product_id']

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)

        wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)
        if not created:
            wishlist_item.delete()
            return Response({"message": "Product removed from wishlist."}, status=200)

        return Response({"message": "Product added to wishlist."}, status=201)




@extend_schema(tags=['user'])
class CartListCreateAPIView(ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartModelSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')

        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise ValidationError({"error": "The product does not exist."})

        if product.quantity <= 0:
            raise ValidationError({"error": "This product is out of stock."})

        existing_cart_item = Cart.objects.filter(user=user, product=product).first()
        if existing_cart_item:
            existing_cart_item.delete()
            product.quantity += 1
            product.save()
            return Response({"message": "Product removed from cart."}, status=status.HTTP_200_OK)

        product.quantity -= 1
        product.save()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
