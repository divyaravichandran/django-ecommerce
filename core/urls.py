
from django.urls import path, include
from .views import HomeView, CheckOut, ItemDetailView, addToCart, products, removeFromCart, OrderSummaryView, removeOneFromCart, PaymentView, CouponView, Refund


app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout', CheckOut.as_view(), name='checkout'),
    path('products', products, name='products'),
    path('product/<slug>', ItemDetailView.as_view(), name='product'),
    path('addToCart/<slug>', addToCart, name='addToCart'),
    path('removeFromCart/<slug>', removeFromCart, name='removeFromCart'),
    path('orderSummary', OrderSummaryView.as_view(), name='orderSummary'),
    path('removeOneFromCart/<slug>', removeOneFromCart, name='removeOneFromCart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('add-coupon', CouponView.as_view(), name='coupon'),
    path('refund', Refund.as_view(), name='refund')

]
