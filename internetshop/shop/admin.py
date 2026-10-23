from django.contrib import admin
from django.db.models import F
from django.shortcuts import redirect

from .models import (
    Category, Collection, ColorOption, Lead, Material, Order, OrderItem,
    Product, ProductImage, Review, SiteSettings,
)

ATTRIBUTION_FIELDS = (
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
    'yclid', 'ym_client_id', 'landing_page',
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Синглтон: список сразу ведёт на единственную запись, добавление/удаление запрещены."""

    fields = (
        'hero_image', 'b2b_image', 'designers_image', 'about_image',
        'promo_enabled', 'promo_text', 'promo_url',
    )

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
    list_display = ('name', 'material', 'category', 'price', 'is_available', 'is_featured', 'is_new', 'is_bestseller')
    list_editable = ('is_new', 'is_bestseller')
    list_filter = ('material', 'category', 'collection', 'is_available', 'is_featured', 'is_new', 'is_bestseller')
    search_fields = ('name', 'sku', 'description', 'tilda_id')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('available_colors',)
    inlines = [ProductImageInline]
    actions = ['enable_sale']

    @admin.action(description='Включить скидку')
    def enable_sale(self, request, queryset):
        n = queryset.filter(sale_price__isnull=False).update(
            old_price=F('price'), price=F('sale_price'), sale_price=None,
        )
        self.message_user(request, f'Скидка включена у товаров: {n}')


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
    list_filter = ('status', 'payment_status', 'telegram_notified', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'customer_email')
    readonly_fields = ('created_at', 'total_price', 'telegram_notified', *ATTRIBUTION_FIELDS)
    inlines = [OrderItemInline]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'lead_type', 'status', 'source_page', 'created_at')
    list_filter = ('lead_type', 'status', 'telegram_notified')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at', 'telegram_notified', *ATTRIBUTION_FIELDS)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'author', 'rating', 'is_published', 'created_at')
    list_filter = ('is_published', 'rating')
    search_fields = ('author', 'product__name')
