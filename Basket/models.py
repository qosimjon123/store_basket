import uuid
from contextlib import nullcontext

from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
class Basket(models.Model):

    class BasketType(models.TextChoices):

        DELIVERY = 'delivery'
        PICKUP = 'pickup'


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.CharField(null=True, blank=True, max_length=50)
    session_id = models.CharField(null=True, blank=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) # type: ignore
    store_id = models.PositiveIntegerField(null=False)
    basket_type = models.CharField(null=True, blank=True, max_length=50)
    customer_latitude = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=8)
    customer_longitude = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=8)
    customer_address = models.TextField(null=True, blank=True)







class BasketItem(models.Model):
    cart = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    product_id = models.IntegerField(null=False, blank=False)
    sku = models.CharField(null=False, blank=False, max_length=100)


    class Meta:
        unique_together = ('cart', 'product_id')




class SyncedDataFromProduct(models.Model):
    store_id = models.PositiveIntegerField(null=False)
    product_id = models.PositiveIntegerField(null=False)
    sku = models.CharField(null=False, blank=False, max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10, null=False)
    discount = models.DecimalField(decimal_places=2, max_digits=10, null=False)
    quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('store_id', 'product_id')

