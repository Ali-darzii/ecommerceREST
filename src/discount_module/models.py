from django.db import models
from utils.manager import NowUntilEndSet
from product_module.models import Product, ProductCategory, ProductBrand
from django.utils import timezone



class DiscountBase(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    # objects = models.Manager()
    # now_until_end_objects = NowUntilEndSet()

    class Meta:
        abstract = True

class ProductDiscount(DiscountBase):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_discount')

    now_until_end_objects = NowUntilEndSet()


    def __str__(self):
        return f"{self.product.title} - {self.percentage}"



class BrandDiscount(DiscountBase):
    brand = models.ForeignKey(ProductBrand, on_delete=models.CASCADE, related_name='brand_discount')
    now_until_end_objects = NowUntilEndSet()
    def __str__(self):
        return f"{self.brand.title} - {self.percentage}"



class CategoryDiscount(DiscountBase):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='category_discount')
    now_until_end_objects = NowUntilEndSet()
    def __str__(self):
        return f"{self.category.title} - {self.percentage}"
