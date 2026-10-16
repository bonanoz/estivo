from django.contrib import admin
from django.shortcuts import redirect

from .models import (
    Category, Collection, ColorOption, Lead, Material, Order, OrderItem,
    Product, ProductImage, Review, SiteSettings,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Синглтон: список сразу ведёт на единственную запись, добавление/удаление запрещены."""

    fields = ('hero_image', 'b2b_image', 'designers_image', 'about_image')

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.get_solo()
        return redirect('admin:shop_sitesettings_change', obj.pk)


@admin.register(ColorOption)
class ColorOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'finish_type', 'hex', 'order')
    list_filter = ('finish_type',)
    search_fields = ('name',)
    ordering = ('finish_type', 'order', 'name')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_featured', 'order')
    list_filter = ('is_featured',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'material', 'category', 'price', 'is_available', 'is_featured')
    list_filter = ('material', 'category', 'collection', 'is_available', 'is_featured')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('available_colors',)
    inlines = [ProductImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'unit_price', 'selected_colors')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'customer_phone', 'status', 'payment_status',
        'total_price', 'created_at',
    )
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'customer_email')
    readonly_fields = ('created_at', 'total_price', 'telegram_notified')
    inlines = [OrderItemInline]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'lead_type', 'status', 'source_page', 'created_at')
    list_filter = ('lead_type', 'status')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at', 'telegram_notified')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'author', 'rating', 'is_published', 'created_at')
    list_filter = ('is_published', 'rating')
    search_fields = ('author', 'product__name')
