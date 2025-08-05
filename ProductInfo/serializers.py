from rest_framework import serializers
from rest_framework.utils import representation

from .models import Product, Brand, Store, Category, SubCategory, PriceHistory, ProductImage, Schedule, Unit, ProductVariant, Inventory


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'title', 'image', 'is_only_warehouse', 'store']


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'title', 'image_url']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order', 'alt_text', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()  # Показывает адрес магазина
    sub_category = serializers.StringRelatedField()  # Показывает название подкатегории
    product_images = ProductImageSerializer(many=True, read_only=True)  # Список доп. картинок

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'internal_sku', 'image', 'product_images', 'store', 'sub_category', 'created_at', 'updated_at']


class StoreSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    
    class Meta:
        model = Store
        fields = ['id', 'brand', 'address', 'city', 'latitude', 'longitude', 'delivery_radius_km', 'is_active', 'is_only_warehouse']


class CategorySerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'store', 'title', 'description', 'image']


class ProductVariantSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'price', 'discount', 'variant_value', 'variant_attributes', 'height', 'width', 'depth', 'barcode', 'weight']


class InventorySerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'variant', 'store', 'quantity', 'reserved', 'damaged']


class ScheduleSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    
    class Meta:
        model = Schedule
        fields = ['id', 'store', 'schedule_type', 'weekday', 'is_working', 'open_time', 'close_time', 'is_retail_open', 'is_delivery_available', 'is_warehouse_open']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.open_time:
            data['open_time'] = instance.open_time.strftime('%H:%M')
        if instance.close_time:
            data['close_time'] = instance.close_time.strftime('%H:%M')
        return data


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'title', 'short_name']


class PriceHistorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    
    class Meta:
        model = PriceHistory
        fields = ['id', 'product', 'store', 'old_price', 'new_price', 'old_discount', 'new_discount', 'changed_at']










class StoreProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    quantity = serializers.IntegerField(source='quantity_value')


    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'store', 'price', 'discount', 'quantity']




class CustomStoreProductForBasketQtyCheckSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    quantity = serializers.IntegerField(source='quantity_value')


    class Meta:
        model = ProductVariant
        fields = ['product', 'store', 'quantity']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'store' in representation:
            store_data = representation['store']
            allowed_fields = ['id']
            store_data = {key: store_data[key] for key in store_data if key in allowed_fields }
            representation['store'] = store_data

        if 'product' in representation:
            product_data = representation['product']
            allowed_fields = ['id']
            product_data = {key: product_data[key] for key in product_data if key in allowed_fields}
            representation['product'] = product_data





        return representation


class ActualPriceInStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['price', 'discount', 'product_id', 'store_id']
