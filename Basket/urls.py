from rest_framework_nested import routers
from Basket.views import BasketViewSet, BasketItemViewSet

router = routers.SimpleRouter()
router.register(r'', BasketViewSet, basename='basket')

basket_router = routers.NestedSimpleRouter(router, r'', lookup='basket')
basket_router.register(r'items', BasketItemViewSet, basename='basket-items')

urlpatterns = router.urls + basket_router.urls
