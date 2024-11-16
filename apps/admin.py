from django.contrib import admin

from apps.models import Category, Product, ProductImage


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductImage)
class ProductModelAdmin(admin.ModelAdmin):
    pass
