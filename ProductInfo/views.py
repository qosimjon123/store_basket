from django_filters import rest_framework as filters
from django.db.models import F
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from ProductInfo.models import Product, Brand, Store, Category, SubCategory, ProductVariant, Inventory, Schedule, Unit
from .serializers import ProductSerializer, BrandSerializer, StoreSerializer, CategorySerializer, SubCategorySerializer, \
    ProductVariantSerializer, InventorySerializer, ScheduleSerializer, UnitSerializer
from .pagination import CustomPagination


class BrandViewSet(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['store__id']


class BrandViewSetOverride(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['store__id']
    pagination_class = None


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    pagination_class = None  # Disable pagination


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.select_related('store').all()
    serializer_class = CategorySerializer


class SubCategoryViewSet(ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('sub_category', 'store').prefetch_related('product_images')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sub_category', 'store']


class ProductVariantFilter(filters.FilterSet):
    product__id = filters.BaseInFilter(field_name='product__id', lookup_expr='in')

    class Meta:
        model = ProductVariant
        fields = ['product__id']


class ProductVariantViewSet(ModelViewSet):
    queryset = ProductVariant.objects.select_related(
        'product__store__brand',  # Загружаем Product, Store и связанный Brand
        'product__sub_category',
    ).prefetch_related(
        'product__product_images'
    ).all()

    pagination_class = CustomPagination
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductVariantFilter

    @action(methods=['get'], detail=False)
    def has_quantity(self, request, *args, **kwargs):
        product_id = request.GET.get('product_id')
        store_id = request.GET.get('store_id')

        if not product_id or not store_id:
            return Response({'error': 'No product or store_id provided'})

        try:
            product_id = int(product_id)
        except ValueError:
            return Response({'error': 'Invalid product id provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Ищем варианты продукта и связанные остатки
        filtered_products = self.queryset.filter(product__id=product_id)
        
        # Фильтруем по складу через Inventory
        inventory_products = []
        for variant in filtered_products:
            inventory = Inventory.objects.filter(variant=variant, store_id=store_id).first()
            if inventory and inventory.quantity > 0:
                inventory_products.append(variant)

        serializer = ProductVariantSerializer(inventory_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetPriceViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product__id']

    @action(detail=False, methods=['get'])
    def bulk(self, request, pk=None):
        product_ids = request.GET.getlist('product_ids')
        store_id = request.GET.get('store_id')

        if not product_ids or not store_id:
            return Response({'error': 'No product or store_id provided'})

        try:
            product_ids = [int(i) for i in product_ids[0].split(',')]
        except ValueError:
            return Response({'error': 'Invalid product id provided'})

        filtered_products = self.queryset.filter(product__id__in=product_ids)
        serializer = self.get_serializer(filtered_products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class InventoryViewSet(ModelViewSet):
    queryset = Inventory.objects.select_related('variant__product', 'store').all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['variant__product__id', 'store__id', 'reserved', 'damaged']


class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.select_related('store__brand').all()
    serializer_class = ScheduleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['store__id', 'schedule_type', 'weekday', 'is_working']


class UnitViewSet(ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    pagination_class = None