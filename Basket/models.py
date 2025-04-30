import uuid
from contextlib import nullcontext

from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
class Basket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.IntegerField(null=True, blank=True)
    session_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    store_id = models.PositiveIntegerField(null=False)






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

