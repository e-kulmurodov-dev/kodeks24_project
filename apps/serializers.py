from rest_framework import serializers
from rest_framework.fields import CharField

from apps.models import Category, Product, CustomUser, Wishlist, Cart, ProductImage


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = 'id', 'first_name', 'last_name', 'email', 'phone_number', 'date_joined'


class CategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = 'id', 'name', 'slug'
        read_only_fields = 'slug',


class ProductModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = 'updated_at', 'created_at', 'description', 'owner',
        read_only_fields = 'slug',

    def to_representation(self, instance: Product):
        repr = super().to_representation(instance)
        repr['category'] = CategoryModelSerializer(instance.category).data['name']
        # repr['owner'] = UserModelSerializer(instance.owner).data
        repr['product_image'] = ProductImageModelSerializer(instance.productimage_set.all(), many=True).data

        return repr


class ProductDetailSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=True)
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'price', 'quantity', 'description',)
        read_only_fields = ('slug',)

    def to_representation(self, instance: Product):
        repr = super().to_representation(instance)
        repr['category'] = CategoryModelSerializer(instance.category).data['name']
        repr['owner'] = UserModelSerializer(instance.owner).data['username']
        repr['product_image'] = ProductImageModelSerializer(instance.productimage_set.all(), many=True).data

        return repr


class ProductImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = 'id', 'image'


class LoginModelSerializer(serializers.ModelSerializer):
    email_or_username = CharField(max_length=255)

    class Meta:
        model = CustomUser
        fields = ('email_or_username', 'password')


class RegisterUserModelSerializer(serializers.ModelSerializer):
    confirm_password = CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = 'username', 'email', 'password', 'confirm_password'

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        confirm_password = attrs.pop('confirm_password')
        if confirm_password != attrs.get('password'):
            raise serializers.ValidationError('Passwords did not match!')
        attrs['password'] = confirm_password
        return attrs


class ActivateUserModelSerializer(serializers.ModelSerializer):
    confirmation_code = CharField(max_length=6)

    class Meta:
        model = CustomUser
        fields = ('email', 'confirmation_code')


class WishlistModelSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = Wishlist
        fields = ('id', 'product_id',)

    def to_representation(self, instance):
        repr = super().to_representation(instance)

        product = instance.product
        repr['product_data'] = {
            'name': product.name,
            'price': product.price,
            'category': product.category.name,
        }
        repr['product_image'] = ProductImageModelSerializer(product.productimage_set.all(), many=True).data
        return repr


class CartModelSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'product_id', 'product', 'user')
        read_only_fields = ('product', 'user')

    def validate_product_id(self, product_id):
        # Ensure the product exists
        if not Product.objects.filter(id=product_id).exists():
            raise serializers.ValidationError("The product does not exist.")
        return product_id

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product_data'] = {
            'name': instance.product.name,
            'price': instance.product.price,
            'category': instance.product.category.name,
            'quantity': instance.product.quantity,
        }
        return representation
