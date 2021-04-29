from django.conf import settings
from django.db import models

# Create your models here.


class Item(models.Model):
    name = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.price}"


class Order_Item(models.Model):
    orderItem = origin = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="iteminfo")


class Order(models.Model):
    user = models..ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered models.BooleanField(default=False)
    orders = models.ManyToManyField(
        Order_Item, blank=True, related_name="items")
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}"
