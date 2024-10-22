from django.contrib import admin
from product_module import models

admin.site.register(models.Product)
admin.site.register(models.ProductGallery)
admin.site.register(models.ProductVisit)
admin.site.register(models.ProductCategory)
admin.site.register(models.ProductBrand)
admin.site.register(models.Comment)
admin.site.register(models.Like)
admin.site.register(models.DisLike)
