from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.fields import CharField

from apps.models import Category, Product, CustomUser


class RegisterUserModelSerializer(serializers.ModelSerializer):
    confirm_password = CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = 'id', 'first_name', 'last_name', 'email', 'password', 'confirm_password'

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        confirm_password = attrs.pop('confirm_password')
        if confirm_password != attrs.get('password'):
            raise serializers.ValidationError('Passwords did not match!')
        attrs['password'] = make_password(confirm_password)
        return attrs


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
        exclude = 'updated_at',
        read_only_fields = 'slug',

    def to_representation(self, instance: Product):
        repr = super().to_representation(instance)
        repr['category'] = CategoryModelSerializer(instance.category).data
        repr['owner'] = UserModelSerializer(instance.owner).data
        return repr


class LoginModelSerializer(serializers.ModelSerializer):
    phone_number = CharField(max_length=13)
    confirmation_code = CharField(max_length=6)

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'confirmation_code')
