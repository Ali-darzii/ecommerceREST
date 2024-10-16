from django.db import models


class ProductCategory(models.Model):
    title = models.CharField(max_length=300, db_index=True)
    urls_title = models.CharField(max_length=300, db_index=True)
    is_active = models.BooleanField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        db_table = "Categories_DB"


class ProductBrand(models.Model):
    title = models.CharField(max_length=300, db_index=True)
    url_title = models.CharField(max_length=200, unique=True, db_index=True)
    is_active = models.BooleanField()

    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'
        db_table = "Brand_DB"

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=300)
    image = models.ImageField(upload_to="image/products/")
    price = models.PositiveIntegerField()
    short_descriptions = models.CharField(max_length=400)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, db_index=True)
    inventory = models.IntegerField()
    category = models.ManyToManyField(
        ProductCategory,
        related_name="product_categories")
    brand = models.ForeignKey(ProductBrand, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        db_table = "products_DB"


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/product-gallery')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Product Gallery'
        verbose_name_plural = 'Product Galleries'
        db_table = "Products_DB"
