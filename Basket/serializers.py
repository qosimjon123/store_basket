from rest_framework import serializers
from .models import Basket, BasketItem




class BasketItemSerializer(serializers.ModelSerializer):
    total_item_price = serializers.SerializerMethodField()


    class Meta:
        model = BasketItem
        fields = ['id', 'quantity', 'product_id', 'total_item_price']
        read_only_fields = ['quantity']

    def get_total_item_price(self, obj):
        context = self.context
        if context.get('error', None):
            return 'Error'

        price_data = context.get('price_data', None)

        if not price_data:
            return 'Price data is missing'

        product_info = next((product for product in price_data if product['product_id'] == obj.product_id), None)

        if not product_info:
            return 'Undefined'

        price = product_info.get('price', 0)
        discount = product_info.get('discount', 0)

        discounted_price = price * (1 - discount / 100)

        return obj.quantity * discounted_price



class BasketSerializer(serializers.ModelSerializer):


    class Meta:
        model = Basket
        fields = ['pk', 'customer_id', 'store_id']

