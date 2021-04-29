from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField


# Create your models here.

CATEGORIES = (
    ('S', 'Shirt'),
    ('SW', 'Sportswear'),
    ('OW', 'Outerwear'))

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'))


class Item(models.Model):
    name = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    discount_price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=2, choices=CATEGORIES)
    label = models.CharField(max_length=2, choices=LABEL_CHOICES)
    description = models.CharField(max_length=100)
    slug = models.SlugField()

    def __str__(self):
        return f"{self.name} - {self.price}"

    def get_absolute_url(self):
        return reverse("core:product", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:addToCart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:removeFromCart", kwargs={'slug': self.slug})


class Order_Item(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="iteminfo")
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} - {self.item.name}"

    def get_total_price(self):
        return self.quantity * self.item.price

    def get_discounted_price(self):
        return self.quantity * self.item.discount_price

    def get_savings_from_discount(self):
        return self.get_total_price() - self.get_discounted_price()

    def get_final_price(self):
        final_price = self.item.price
        if self.item.discount_price:
            final_price = self.item.discount_price
        return (final_price * self.quantity)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(
        Order_Item, blank=True, related_name="items")
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()
    billing_address = models.ForeignKey(
        'Billing_Address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    refCode = models.CharField(max_length=10, blank=True, null=True)

    delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}"

    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total = total + order_item.get_final_price()
        discount = 0
        if self.coupon is not None:
            discount = self.coupon.discount

        total -= discount
        return total


class Billing_Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street = models.CharField(max_length=100)
    apartment = models.CharField(max_length=100)
    country = CountryField(multiple=True)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}"


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)
    total = models.FloatField()

    def __str__(self):
        return f"{self.user.username}"


class Coupon(models.Model):
    code = models.CharField(max_length=30)
    discount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.code}"
