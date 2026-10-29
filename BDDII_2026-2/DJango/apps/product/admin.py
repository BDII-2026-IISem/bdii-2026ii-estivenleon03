from django.contrib import admin

from .models import Product, ProductType


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'product_type', 'price', 'stock', 'min_stock', 'is_active')
    list_filter = ('is_active', 'product_type')
    search_fields = ('name', 'brand', 'product_type__name')
    autocomplete_fields = ('product_type',)
    list_select_related = ('product_type',)
