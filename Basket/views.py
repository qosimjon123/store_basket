import decimal
from functools import cached_property
from django.contrib.sites import requests
from django.db.models import Q, Subquery, OuterRef
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
from .models import SyncedDataFromProduct

from pprint import pprint



from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import requests
from .models import Basket
from .serializers import BasketSerializer  # Предполагаю, что у тебя есть сериализатор
from django.core.exceptions import ObjectDoesNotExist

class BasketViewSet(viewsets.ModelViewSet):
    serializer_class = BasketSerializer

    @cached_property
    def queryset(self):
        return Basket.objects.filter(is_active=True).all()

    def get_queryset(self):
        return self.queryset

    def create(self, request, *args, **kwargs):
        """
        При создании товара в корзине автоматически присваиваем корзину.
        Для авторизованных пользователей используем customer_id, для неавторизованных — session_id.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            if request.user.is_authenticated:
                customer_id = request.user.id
                session_id = None
            else:
                session_id = request.headers.get('session')
                customer_id = None
                if not session_id:
                    raise ValidationError({"session": "Session ID is required for anonymous users"})

            if customer_id:
                customer_response = requests.get(
                        "{}/customer/{}".format(customer,validated_data.get("customer_id")))
                if customer_response.status_code != 200:
                    raise ValidationError({"customer": "Customer was not found or blocked"})

            try:
                store_data = SyncedDataFromProduct.objects.filter(
                    store_id=validated_data.get("store_id")
                )
            except ObjectDoesNotExist:
                raise ValidationError({"store": "Магазин не найден"})

            basket, created = Basket.objects.get_or_create(
                customer_id=customer_id,
                session_id=session_id,
                store_id=validated_data.get("store_id"),
                defaults={'is_active': True}
            )

            serializer = self.get_serializer(basket)
            headers = self.get_success_headers(serializer.data)
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(serializer.data, status=status_code, headers=headers)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class BasketItemViewSet(viewsets.ModelViewSet):
    serializer_class = BasketItemSerializer

    @cached_property
    def queryset(self):
        return BasketItem.objects.select_related('cart').filter(cart__id=self.kwargs["basket_pk"], cart__is_active=True)



    def get_queryset(self):
        return self.queryset


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({"error": "Basket not found"}, status=status.HTTP_404_NOT_FOUND)

        store_id = queryset[0].cart.store_id
        print(queryset)

        product_ids = [item.product_id for item in queryset]

        # Получаем данные о наличии товаров
        stock_data = SyncedDataFromProduct.objects.filter(
            store_id=store_id, product_id__in=product_ids
        )
        if not stock_data or len(stock_data) < len(product_ids):
            raise ValidationError({"error": "No stock data available for basket items"})

        # Создаем словарь с доступным количеством для каждого товара
        stock_quantity = {item.product_id: item.quantity for item in stock_data}

        for item in queryset:
            available_quantity = stock_quantity.get(item.product_id, 0)
            if item.quantity > available_quantity:
                item.quantity = available_quantity
                item.save(update_fields=['quantity'])

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Добавляем информацию о доступном количестве к каждому товару
        for item in data:
            item['stock_quantity'] = stock_quantity.get(item['product_id'], 0)

        # Вычисляем общую сумму
        total_sum = sum(
            item['total_item_price']
            for item in data if isinstance(item['total_item_price'], (int, float, decimal.Decimal))
        )

        response_data = {
            'items': data,
            'store_id': store_id,
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

        basket_id = self.kwargs.get('basket_pk')

        try:
            basket = get_object_or_404(Basket, id=basket_id)
            store_id = basket.store_id

            store_data = (SyncedDataFromProduct.objects.
                          filter(store_id=store_id, product_id=validated_data.get("product_id")).all())
            store_data = list(store_data.values())


            if not store_data or not store_data[0].get('quantity', None):
                raise ValidationError(
                        {"store_product": "Product was not found or has empty quantity"},
                )



            validated_data['cart'] = basket
            validated_data['sku'] = store_data[0]['sku']
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
            return Response({"error": "An unexpected error occurred: {}".format(str(e))},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """
        Обновляет количество товара в корзине. Принимает delta (+1 или -1).
        Если quantity становится <= 0, удаляет запись.
        """
        msg_for_customer = []
        instance = self.get_object()  # Получаем существующий BasketItem
        delta = request.data.get('delta', 0)  # Получаем изменение количества (+1 или -1)

        try:
            # Проверяем, что delta — это +1 или -1
            if delta not in [-1, 1]:
                raise ValidationError({"delta": "Delta must be +1 or -1"})

            basket = self.kwargs.get('basket_pk')
            basket_store_id = Basket.objects.filter(id=basket).first().store_id

            if not basket_store_id:
                raise ValidationError({"basket": "Basket was not found or blocked"})

            # Проверяем доступное количество на складе
            checked_quantity = SyncedDataFromProduct.objects.filter(
                product_id=instance.product_id, store_id=basket_store_id
            ).first().quantity

            new_quantity = instance.quantity + delta
            if checked_quantity < new_quantity:
                msg_for_customer.append(f"You have {checked_quantity} items remaining.")
                new_quantity = checked_quantity

            if new_quantity <= 0:
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                instance.quantity = new_quantity
                instance.save()

            # Сериализуем обновленный объект
            serializer = self.get_serializer(instance)
            # Формируем ответ, добавляя stock_quantity
            response_data = serializer.data
            response_data['stock_quantity'] = checked_quantity

            if msg_for_customer:
                response_data['message'] = msg_for_customer

            return Response(response_data, status=status.HTTP_200_OK)

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
        price_data = SyncedDataFromProduct.objects.filter(store_id=store_id, product_id__in=products_id).values()



        try:

            data = list(price_data)
        except requests.exceptions.RequestException as e:
            return {"error": "Error fetching price data from external service"}

        return {'price_data': data}
