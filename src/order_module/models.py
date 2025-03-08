from django.db import models
from auth_module.models import User
from product_module.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order')
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True)
    total_products = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.phone_no}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        db_table = "Order_DB"

    def calculate_total_price(self):
        total_price = 0
        for order_detail in self.detail_order.all():
            total_price += order_detail.final_price
        self.total_price = total_price
        self.save()

    def calculate_final_price(self):
        for order_detail in self.detail_order.all():
            order_detail.final_price = order_detail.product.price * order_detail.count
            self.save()
        self.save()

    def count_total_products(self):
        count = 0
        for order_detail in self.detail_order.all():
            count += order_detail.count


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="detail_order")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_order")
    count = models.IntegerField(default=0)
    final_price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.order.user.phone_no} | {self.product.title}"

    class Meta:
        verbose_name = "Order Detail"
        verbose_name_plural = "Order Details"
        db_table = "OrderDetail_DB"



@receiver(signal=post_save, sender=User)
def create_user_logins(sender, created, instance, **kwargs):
    """ create order obj after user created """
    if created and isinstance(instance, User):
        Order.objects.create(user=instance)