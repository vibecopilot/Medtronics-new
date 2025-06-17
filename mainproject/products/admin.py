from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, ProductCategory, ProductType, Product,
    Subproduct, Region, OrderProductOnline, SearchProduct
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    search_fields = ['name']
    list_filter = ['category']

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_category']
    list_filter = ['product_category']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_type', 'image_tag', 'created_at']
    list_filter = ['product_type']
    search_fields = ['name', 'description']
    readonly_fields = ['image_preview']

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:contain;" />', obj.image.url)
        return "-"
    image_tag.short_description = "Image"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" style="object-fit:contain;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image Preview"


@admin.register(Subproduct)
class SubproductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'unit']
    list_filter = ['product']
    search_fields = ['name']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['country_code', 'country_name']
    search_fields = ['country_name', 'country_code']
    ordering = ['country_name']

@admin.register(OrderProductOnline)
class OrderProductOnlineAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'region', 'status', 'order_date']
    list_filter = ['status', 'region']
    search_fields = ['user__username', 'product__name', 'number']

@admin.register(SearchProduct)
class SearchProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']
    search_fields = ['user__username', 'product__name']
