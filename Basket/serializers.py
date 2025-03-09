from rest_framework import serializers
from .models import Basket, BasketItem
import requests

class BasketSerializer(serializers.ModelSerializer):


    class Meta:
        model = Basket
        fields = ['pk', 'customer_id', 'store_id']



class BasketItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    cart = BasketSerializer(read_only=True)



    class Meta:
        model = BasketItem
        fields = ['id','quantity', 'product_id', 'total_price', 'cart']
        read_only_fields = ['quantity']

    def get_total_price(self, obj):
        cart_store = obj.cart.store_id  # Используем правильную связь через `cart`
        price_url = "http://127.0.0.1:8005/api/price/?product__id={}&store__id={}" \
            .format(
            obj.product_id,
            cart_store  # Исправлено: передаем правильный store_id
        )
        response = requests.get(price_url)

        return obj.quantity * response.json()[0].get('price')


