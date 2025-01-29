from django.db import models
import math

from product_module.models import Product


class ProductDiscount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_discount')
    is_active = models.BooleanField(default=True)
    discount_percentage = models.PositiveIntegerField(max_length=100)




    def __str__(self):
        return f"{self.product.title} - {self.discount_percentage}"

    class Meta:
        verbose_name = "ProductDiscount"
        verbose_name_plural = "ProductDiscounts"
        db_table = "ProductDiscount_DB"

