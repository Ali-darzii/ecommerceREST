from django.db import models

from utils.utils import rest_of_percentage
from auth_module.models import User
from utils.manager import IsActiveSet, NowUntilEndSet
from django.utils.functional import cached_property
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class ProductCategory(models.Model):
    title = models.CharField(max_length=300, db_index=True)
    urls_title = models.CharField(max_length=300, db_index=True)
    is_active = models.BooleanField()

    objects = models.Manager()
    active_objects = IsActiveSet()

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

    objects = models.Manager()
    active_objects = IsActiveSet()

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

    objects = models.Manager()
    active_objects = IsActiveSet()

    @property
    def available(self):
        return self.inventory > 0

    @cached_property
    def active_discount(self):
        """ priority: ProductDiscount > BrandDiscount > CategoryDiscount  """
        from discount_module.models import ProductDiscount, BrandDiscount, CategoryDiscount

        discount = ProductDiscount.now_until_end_objects.filter(product=self).first()
        if discount:
            return discount
        discount = BrandDiscount.now_until_end_objects.filter(brand__product=self).first()
        if discount:
            return discount
        discount = CategoryDiscount.now_until_end_objects.filter(category__in=self.category.all()).first()
        if discount:
            return discount
        return None

    @property
    def discount(self):
        product_discount = self.active_discount
        return product_discount.percentage if product_discount else 0

    @property
    def final_price(self):
        product_discount = self.active_discount
        if product_discount:
            return rest_of_percentage(self.price, product_discount.percentage)
        return self.price

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        db_table = "products_DB"


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_gallery")
    image = models.ImageField(upload_to='images/product-gallery')

    objects = models.Manager()

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Product Gallery'
        verbose_name_plural = 'Product Galleries'
        db_table = "Galleries_DB"


class ProductVisit(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ip = models.CharField(max_length=30)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f"{self.product.title} | {self.ip}"

    class Meta:
        verbose_name = 'Product Visit'
        verbose_name_plural = 'Product Visits'


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_comment")
    parent = models.ForeignKey("Comment", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    @property
    def like_count(self):
        return self.likes.user.count()

    @property
    def dislike_count(self):
        return self.dislikes.user.count()

    def __str__(self):
        return f"{self.product.title} | {self.user.phone_no}"

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        db_table = "Comment_DB"


class Like(models.Model):
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ManyToManyField(User, related_name="user_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.comment.body}"

    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = "Likes"
        db_table = "Likes_DB"


class DisLike(models.Model):
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name="dislikes")
    user = models.ManyToManyField(User, related_name="user_dislikes")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.comment.body}"

    class Meta:
        verbose_name = 'DisLike'
        verbose_name_plural = "DisLikes"
        db_table = "DisLikes_DB"


@receiver(post_save, sender=Comment)
def create_comment_like_dislike(sender, instance, created, **kwargs):
    if created and isinstance(instance, Comment):
        Like.objects.create(comment=instance)
        DisLike.objects.create(comment=instance)
