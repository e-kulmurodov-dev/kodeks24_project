from django.contrib import admin

from apps.models import Category, Product, ProductImage, CustomUser
from apps.models.products import Cart, Wishlist


class BasePermission(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff


class PhotosStackedInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    min_num = 1
    max_num = 3


@admin.register(Product)
class ProductAdmin(BasePermission):
    list_display = ['id', 'name', 'price', 'description']
    ordering = ['id']
    list_display_links = ['name']
    search_fields = ['name']
    autocomplete_fields = ['category']
    inlines = [PhotosStackedInline, ]


@admin.register(Category)
class CategoryModelAdmin(BasePermission):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(ProductImage)
class ProductImageModelAdmin(BasePermission):
    pass


@admin.register(Cart)
class CartModelAdmin(BasePermission):
    list_display = ['user', 'product']


@admin.register(Wishlist)
class CartModelAdmin(BasePermission):
    list_display = ['user', 'product']


@admin.register(CustomUser)
class CustomUserAdmin(BasePermission):
    list_display = ('email', 'phone_number', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    search_fields = ('email', 'phone_number',)
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            return (
                (None, {'fields': ('email', 'phone_number')}),
                ('Important dates', {'fields': ('last_login', 'date_joined')}),
            )
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('is_superuser', 'is_staff')
        return ()
