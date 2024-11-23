from django.db.models import Model, CharField, IntegerField, ForeignKey, CASCADE, ImageField, PositiveIntegerField, \
    DateTimeField
from django_ckeditor_5.fields import CKEditor5Field

from apps.models import SlugBaseModel, TimeBaseModel

class Category(SlugBaseModel):
    name = CharField(max_length=255)

class Product(SlugBaseModel, TimeBaseModel):
    price = IntegerField()
    category = ForeignKey('apps.Category', CASCADE, related_name='products')
    quantity = PositiveIntegerField(default=0, db_default=0)
    owner = ForeignKey('apps.CustomUser', CASCADE)
    description = CKEditor5Field(null=True, blank=True)


class ProductImage(Model):
    image = ImageField(upload_to='product/images/%Y/%m/%d')
    product = ForeignKey('apps.Product', CASCADE)

    def __str__(self):
        return f"Image for {self.product.name}"

class Wishlist(TimeBaseModel):
    product = ForeignKey("apps.Product", CASCADE)
    user = ForeignKey("apps.CustomUser", CASCADE)

    class Meta:
        unique_together = ('product', 'user')


class Cart(Model):
    user = ForeignKey('CustomUser', on_delete=CASCADE, related_name='cart')
    product = ForeignKey(Product, on_delete=CASCADE, related_name='cart')
    quantity = PositiveIntegerField(default=1)
    added_on = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')