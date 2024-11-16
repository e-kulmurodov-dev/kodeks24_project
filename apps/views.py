from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny

from apps.models import CustomUser, Category, Product
from apps.pagination import CustomPagination
from apps.serializers import UserModelSerializer, CategoryModelSerializer, ProductModelSerializer, \
    RegisterUserModelSerializer


class UserListAPIView(ListCreateAPIView):
    queryset = CustomUser.objects.order_by('id')
    serializer_class = UserModelSerializer
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryModelSerializer


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductModelSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']
    # permission_classes = IsAuthenticated,


class RegisterCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterUserModelSerializer
    permission_classes = AllowAny,