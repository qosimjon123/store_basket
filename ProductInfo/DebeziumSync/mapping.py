from ProductInfo.models import (
    Brand, Store, Schedule, Category, SubCategory, Unit, Product,
    ProductImage, ProductVariant, Inventory
)

TABLE_MODEL_MAPPING = {
        'Brands': Brand,
        'Stores': Store,
        'schedules': Schedule,
        'Categories': Category,
        'SubCategories': SubCategory,
        'Units': Unit,
        'Products': Product,
        'Product_images': ProductImage,
        'Product_variants': ProductVariant,
        'Inventory': Inventory,
    }


BASE64_FIELDS = {
        'Stores': ['latitude', 'longitude', 'delivery_radius_km'],
        'Product_variants': ['height', 'width', 'depth', 'price'],

    }



# TIMESTAMP_FIELDS = {
#         'Brands': ['created_at', 'updated_at'],
#         'Categories': ['created_at', 'updated_at'],
#         'SubCategories': ['created_at', 'updated_at'],
#         'Units': ['created_at', 'updated_at'],
#         'Product_images': ['created_at'],
#         'Products': ['created_at', 'updated_at'],
#     }

TIME_FIELDS = {
        'schedules': ['open_time', 'close_time'],
    }


FIELD_MAPPING = {
    'Brands': {
        'id': 'id',
        'title': 'title',
        'image': 'image',
        'is_only_warehouse': 'is_only_warehouse',
    },
    'Stores': {
        'id': 'id',
        'brand': 'brand_id',  # Пример несоответствия: в сообщении 'brand_id', в модели 'brand'
        'address': 'address',
        'city': 'city',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'delivery_radius_km': 'delivery_radius_km',
        'is_active': 'is_active',
        'is_only_warehouse': 'is_only_warehouse',
        'schedule_type': 'schedule_type',
    },
    'schedules': {
        'id': 'id',
        'weekday': 'weekday',
        'is_working': 'is_working',
        'open_time': 'open_time',
        'close_time': 'close_time',
        'store_id': 'store_id',
        'is_delivery_available': 'is_delivery_available',
        'is_retail_open': 'is_retail_open',
        'is_warehouse_open': 'is_warehouse_open',
        'schedule_type': 'schedule_type',
    },
    'Categories': {
        'id': 'id',
        'title': 'title',
        'description': 'description',
        'image': 'image',
        'store_id': 'store_id',  # Оставляем как store_id, Django сам найдет Store
    },
    'SubCategories': {
        'id': 'id',
        'title': 'title',
        'image_url': 'image_url',
        'category_id': 'category_id',  # Пример: в сообщении 'category_id', в модели ForeignKey 'category'
    },
    'Units': {
        'id': 'id',
        'title': 'title',
        'short_name': 'short_name',
    },
    'Products': {
        'id': 'id',
        'title': 'title',
        'description': 'description',
        'options': 'options',
        'internal_sku': 'internal_sku',
        'image': 'image',
        'group_id': 'group_id',
        'sub_category_id': 'sub_category_id',
        'store_id': 'store_id',
        'unit_id': 'unit_id',
        'age_restriction': 'age_restriction',
    },
    'Product_images': {
        'id': 'id',
        'product_id': 'product_id',
        'image': 'image',
        'order': 'order',
        'alt_text': 'alt_text',
    },
    'Product_variants': {
        'id': 'id',
        'product_id': 'product_id',
        'price': 'price',
        'discount': 'discount',
        'variant_value': 'variant_value',
        'variant_attributes': 'variant_attributes',
        'height': 'height',
        'width': 'width',
        'depth': 'depth',
        'barcode': 'barcode',
        'weight': 'weight',
    },
    'Inventory': {
        'id': 'id',
        'quantity': 'quantity',
        'reserved': 'reserved',
        'damaged': 'damaged',
        'variant_id': 'variant_id',
        'store_id': 'store_id',
    },
}


IGNORE_FIELDS = [
    'created_at', 'updated_at'
]