from pprint import pprint
from django.contrib import admin
from ProductInfo.models import Brand, Store, Category, SubCategory, Product, PriceHistory, ProductImage, Schedule, Unit, ProductVariant, Inventory
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .resources import SubCategoryResource, CategoryResource, BrandResource, ProductImageResource, PriceHistoryResource, \
    StoreResource, ProductResource, ScheduleResource, UnitResource, ProductVariantResource, InventoryResource


@admin.register(SubCategory)
class SubCategoryAdmin(ImportExportModelAdmin):
    resource_class = SubCategoryResource
    search_fields = ['title']


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ['id', 'title', 'store', 'logo_display_readonly']
    readonly_fields = ['logo_display_readonly', ]
    search_fields = ['title', 'store__address']

    def logo_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image)
        return "Нет логотипа"

    def logo_display_readonly(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" />', obj.image)
        return "Нет логотипа"


@admin.register(Brand)
class BrandAdmin(ImportExportModelAdmin):
    resource_class = BrandResource
    list_display = ['id', 'title', 'logo_display']
    readonly_fields = ['logo_display_readonly']

    def logo_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image)
        return "Нет логотипа"

    def logo_display_readonly(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" />', obj.image)
        return "Нет логотипа"

    logo_display_readonly.short_description = 'Logo Preview'


@admin.register(ProductImage)
class ProductImageAdmin(ImportExportModelAdmin):
    resource_class = ProductImageResource
    list_display = ['id', 'product', 'image', 'order', 'created_at']
    search_fields = ['product__title']
    list_filter = ['created_at']

    fieldsets = (
        (None, {
            'fields': ('product', 'image', 'order', 'alt_text')
        }),
        ('Date Information', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['created_at']


@admin.register(PriceHistory)
class PriceHistoryAdmin(ImportExportModelAdmin):
    resource_class = PriceHistoryResource
    list_display = ('id', 'product', 'store', 'old_price', 'new_price', 'changed_at')
    list_filter = ['changed_at']
    search_fields = ['product__title', 'store__address']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'store', 'store__brand')


@admin.register(Store)
class StoreAdmin(ImportExportModelAdmin):
    resource_class = StoreResource
    list_display = ('id', 'brand', 'address', 'city', 'is_active', 'is_only_warehouse')
    search_fields = ['address', 'city']
    list_filter = ['is_active', 'is_only_warehouse', 'brand']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('brand')


@admin.register(Schedule)
class ScheduleAdmin(ImportExportModelAdmin):
    resource_class = ScheduleResource
    list_display = ['id', 'store', 'schedule_type', 'weekday', 'is_working', 'open_time_display', 'close_time_display']
    list_filter = ['schedule_type', 'weekday', 'is_working', 'store__brand']
    search_fields = ['store__address', 'store__brand__title']
    ordering = ['store', 'schedule_type', 'weekday']

    def open_time_display(self, obj):
        if obj.open_time:
            return obj.open_time.strftime('%H:%M')
        return '-'
    open_time_display.short_description = 'Время открытия'

    def close_time_display(self, obj):
        if obj.close_time:
            return obj.close_time.strftime('%H:%M')
        return '-'
    close_time_display.short_description = 'Время закрытия'


@admin.register(Unit)
class UnitAdmin(ImportExportModelAdmin):
    resource_class = UnitResource
    list_display = ['title', 'short_name']
    search_fields = ['title', 'short_name']


@admin.register(ProductVariant)
class ProductVariantAdmin(ImportExportModelAdmin):
    resource_class = ProductVariantResource
    list_display = ['id', 'product', 'variant_value', 'price', 'discount', 'barcode']
    list_filter = ['discount', 'product__store__brand']
    search_fields = ['product__title', 'variant_value', 'barcode']
    autocomplete_fields = ['product']


@admin.register(Inventory)
class InventoryAdmin(ImportExportModelAdmin):
    resource_class = InventoryResource
    list_display = ['id', 'variant', 'store', 'quantity', 'reserved', 'damaged']
    list_filter = ['reserved', 'damaged', 'store__brand']
    search_fields = ['variant__product__title', 'store__address']
    autocomplete_fields = ['variant', 'store']


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ['id', 'age_restriction', 'title', 'store', 'sub_category', 'logo_display_readonly']
    readonly_fields = ['logo_display_readonly', 'other_images_display_readonly']
    search_fields = ['title', 'internal_sku', 'group_id']
    list_filter = ['store__brand', 'sub_category__category']
    autocomplete_fields = ['sub_category', 'store', 'unit']

    def logo_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image)
        return "Нет логотипа"

    def logo_display_readonly(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" />', obj.image)
        return "Нет логотипа"

    logo_display_readonly.short_description = 'Logo Preview'

    def other_images_display_readonly(self, obj):
        images = obj.product_images.all()
        if images:
            image_html = ''.join(
                [format_html('<img src="{}" width="50" height="50" />', image.image) for image in images]
            )
            return format_html(image_html)
        return "Нет дополнительных изображений"

