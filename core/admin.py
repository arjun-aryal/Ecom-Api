from django.contrib import admin
from .models import User, SellerProfile, Category, Product, Order, OrderItem, InventoryLog, Review


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    search_fields = ['username', 'email']
    list_filter =  ['role', 'is_staff']
    fieldsets = (
        (None, {
            'fields': ('first_name', 'username', 'email', 'password')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    # remove help text
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in form.base_fields.values():
            field.help_text = ''
        return form


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'user', 'contact_num']
    search_fields = ['shop_name', 'user__username']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'seller', 'price', 'stock_quantity']
    list_filter = ['category', 'seller']
    search_fields = ['name', 'description']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['product__name', 'customer__username']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order_date', 'status', 'is_paid']
    list_filter = ['status', 'is_paid']
    search_fields = ['customer__username']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    search_fields = ['order__customer__username', 'product__name']

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_change', 'reason', 'created_at']
    list_filter = ['reason']
    search_fields = ['product__name']