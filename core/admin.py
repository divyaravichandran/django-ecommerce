from django.contrib import admin
from .models import Item, Order, Order_Item, Billing_Address, Payment, Coupon

# Register your models here.


def update_refund_status(modeladmin, request, queryset):
    queryset.update(refund_processed=True)
    queryset.update(refund_requested=False)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'ordered', 'delivered',
                    'received',
                    'refund_requested',
                    'refund_processed',
                    'refCode')
    actions = [update_refund_status]


admin.site.register(Order, OrderAdmin)
admin.site.register(Item)
admin.site.register(Order_Item)
admin.site.register(Billing_Address)
admin.site.register(Payment)
admin.site.register(Coupon)
