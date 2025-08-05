from django.urls import path
from django.urls.conf import include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register('product', views.ProductViewSet)
router.register('category', views.CategoryViewSet)
router.register('subcategory', views.SubCategoryViewSet)
router.register('brand', views.BrandViewSet)
router.register('brands', views.BrandViewSetOverride, basename='brands')
router.register('store', views.StoreViewSet)
router.register('product-variant', views.ProductVariantViewSet)
router.register('price', views.GetPriceViewSet, basename='price')
router.register('inventory', views.InventoryViewSet)
router.register('schedule', views.ScheduleViewSet)
router.register('unit', views.UnitViewSet)

urlpatterns = router.urls