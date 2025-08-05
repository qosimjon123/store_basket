from import_export import resources
from import_export.fields import Field
from .models import Brand, Store, Category, SubCategory, Product, PriceHistory, ProductImage, Schedule, Unit, ProductVariant, Inventory

class BrandResource(resources.ModelResource):
    class Meta:
        model = Brand

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category

class SubCategoryResource(resources.ModelResource):
    class Meta:
        model = SubCategory

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product

class StoreResource(resources.ModelResource):
    class Meta:
        model = Store

class PriceHistoryResource(resources.ModelResource):
    class Meta:
        model = PriceHistory

class ProductImageResource(resources.ModelResource):
    class Meta:
        model = ProductImage

class ScheduleResource(resources.ModelResource):
    class Meta:
        model = Schedule
        import_id_fields = ['id']
        export_order = ['id', 'store', 'schedule_type', 'weekday', 'is_working', 'open_time', 'close_time', 'is_retail_open', 'is_delivery_available', 'is_warehouse_open']

class UnitResource(resources.ModelResource):
    class Meta:
        model = Unit

class ProductVariantResource(resources.ModelResource):
    class Meta:
        model = ProductVariant

class InventoryResource(resources.ModelResource):
    class Meta:
        model = Inventory



