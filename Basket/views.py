from functools import cached_property
from django.contrib.sites import requests
from requests import RequestException
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import get_object_or_404
import requests
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from .models import Basket, BasketItem
from .serializers import BasketSerializer, BasketItemSerializer
from .sourcesUrls import customer, ecommerce

from pprint import pprint



class BasketViewSet(viewsets.ModelViewSet):

    serializer_class = BasketSerializer

    @cached_property
    def queryset(self):
        return Basket.objects.all()



    def get_queryset(self):
        return self.queryset




    def create(self, request , *args, **kwargs):
        """
        При создании товара в корзине автоматически присваиваем корзину.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:

            customer_response = requests.get(
                "{}/customer/{}".format(customer,validated_data.get("customer_id")))
            if customer_response.status_code != 200:
                raise ValidationError(
                    {"customer": "Customer was not found or blocked"},
                )

            store_response = requests.get('{}/api/store/{}'.format(ecommerce,validated_data.get("store_id")))
            if store_response.status_code != 200:
                raise ValidationError(
                    {"store": "Магазин не найден"},
                )

            basket, created = Basket.objects.get_or_create(
                customer_id=validated_data.get("customer_id"),
                store_id=validated_data.get("store_id")
            )

            if created:
                serializer = self.get_serializer(basket)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                serializer = self.get_serializer(basket)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)



class BasketItemViewSet(viewsets.ModelViewSet):
    serializer_class = BasketItemSerializer

    @cached_property
    def queryset(self):
        return BasketItem.objects.select_related('cart').filter(cart__id=self.kwargs["basket_pk"])


    def get_queryset(self):
        return self.queryset



    def list(self, request, *args, **kwargs):

        queryset = self.queryset
        serializer = self.get_serializer(queryset, many=True)

        data = serializer.data
        if not data:
            return Response({"error": "Basket not found"}, status=status.HTTP_404_NOT_FOUND)

        total_sum = sum([
            item['total_item_price']
            for item in data if isinstance(item['total_item_price'], (int, float))
        ])

        response_data = {
            'items': data,
            'total_sum': total_sum,
        }

        return Response(response_data, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        """
        При создании товара в корзине автоматически присваиваем корзину.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Получаем id корзины
        basket_id = self.kwargs.get('basket_pk')

        try:
            # Получаем корзину по basket_id
            basket = get_object_or_404(Basket, id=basket_id)
            store_id = basket.store_id


            # Проверяем наличие продукта в магазине
            product_response = requests.get(
                "{}/api/storeproduct/has_quantity/?product_id={}&store_id={}".format(
                   ecommerce,
                    validated_data.get("product_id"),
                    store_id
                )
            ).json()


            if not product_response:
                raise ValidationError(
                        {"store_product": "Product was not found"}
                )


            product_response = product_response[0].get('quantity', None)
            print(product_response)
            if not product_response or product_response == 0:
                raise ValidationError(
                    {"store_product": "Product has empty quantity"}
                )







            validated_data['cart'] = basket
            serializer.save()

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)




        except ValidationError as e:
            # Обработка ошибок валидации
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except RequestException as e:
            # Ошибка при запросе к внешнему сервису
            return Response({"error": "Error connecting to the store service"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # Неожиданные ошибки
            return Response({"error": "An unexpected error occurred: {}".format(str(e))},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """
        Обновляет количество товара в корзине. Принимает delta (+1 или -1).
        Если quantity становится <= 0, удаляет запись.
        """
        instance = self.get_object()  # Получаем существующий BasketItem
        delta = request.data.get('delta', 0)  # Получаем изменение количества (+1 или -1)

        try:
            # Проверяем, что delta — это +1 или -1
            if delta not in [-1, 1]:
                raise ValidationError({"delta": "Delta must be +1 or -1"})

            # Обновляем количество
            new_quantity = instance.quantity + delta
            if new_quantity <= 0:
                # Если quantity <= 0, удаляем запись
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                # Обновляем quantity и сохраняем
                instance.quantity = new_quantity
                instance.save()

            # Сериализуем обновленный объект
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_serializer_context(self):
        queryset = self.get_queryset()

        if not queryset:
            return {}

        store_id = queryset[0].cart.store_id
        products_id = [i.product_id for i in queryset]

        price_url = "{}/api/price/bulk/?product_ids={}&store_id={}".format(
            ecommerce,
            ','.join(str(item) for item in products_id),
            store_id
        )

        try:
            data = requests.get(price_url).json()
        except requests.exceptions.RequestException as e:
            return {"error": "Error fetching price data from external service"}

        return {'price_data': data}
