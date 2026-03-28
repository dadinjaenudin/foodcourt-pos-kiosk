from django.contrib import admin
from django.utils.html import format_html
from .models import Tenant, Category, Product, Order, OrderItem


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['stall_number', 'name', 'cuisine_type', 'is_open', 'is_active', 'rating', 'total_orders', 'logo_preview']
    list_editable = ['is_open', 'is_active']
    list_filter = ['is_active', 'is_open', 'cuisine_type']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;">', obj.logo.url)
        return "No logo"
    logo_preview.short_description = 'Logo'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'name', 'order']
    list_filter = ['tenant']
    ordering = ['tenant', 'order', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'category', 'price', 'is_available', 'is_featured', 'is_bestseller', 'image_preview']
    list_editable = ['is_available', 'is_featured', 'is_bestseller', 'price']
    list_filter = ['tenant', 'category', 'is_available', 'is_featured', 'is_bestseller', 'is_spicy', 'is_vegetarian']
    search_fields = ['name', 'description']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;">', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'unit_price', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'tenant', 'customer_name', 'table_number', 'status', 'payment_method', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'tenant']
    search_fields = ['order_number', 'customer_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
