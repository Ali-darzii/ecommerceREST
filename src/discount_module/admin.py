from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.ProductDiscount)
admin.site.register(models.BrandDiscount)
admin.site.register(models.CategoryDiscount)