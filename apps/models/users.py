from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField, ManyToManyField

from apps.models.managers import CustomUserManager


class CustomUser(AbstractUser):
    phone_number = CharField(max_length=25, unique=True, null=True)
    email = EmailField(max_length=255, blank=True, null=True, unique=True)
    wishes = ManyToManyField('apps.Product', blank=True)
    password = CharField(max_length=150,)
    username = CharField(max_length=150, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
