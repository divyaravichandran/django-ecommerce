from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Order, Order_Item, Payment, Billing_Address, Coupon
from django.views.generic import ListView, DetailView, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib import messages
from .forms import CheckoutForm, CouponForm, RefundForm
from django.conf import settings
import stripe
import string
import random

stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
# settings.STRIPE_SECRET_KEY
# Create your views here.


def item_list(request):
    context = {
        "itemlist": Item.objects.all()
    }
    return render(request, "home-page.html", context)


def get_random():

    return ''.join(random.choices(string.ascii_uppercase +
                                  string.digits, k=10))


def checkout(request):
    return render(request, "checkout.html")


def products(request):
    return render(request, "product-page.html")


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


class OrderSummaryView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                "object": order
            }
        except ObjectDoesNotExist:
            messages.error(self.request, "No items in cart!")
            return redirect("/")
        return render(self.request, "order-summary.html", context)


class CheckOut(View):

    def get(self, *args, **kwargs):
        order = Order.objects.get(
            user=self.request.user, ordered=False)

        form = CheckoutForm()
        couponForm = CouponForm()
        context = {
            "form": form,
            "couponForm": couponForm,
            "order": order

        }
        return render(self.request, "checkout.html", context)

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                print(form.cleaned_data)
                street = form.cleaned_data.get("street")
                apartment = form.cleaned_data.get("apartment")
                country = form.cleaned_data.get("country")
                zip = form.cleaned_data.get("zip")
                same_billing_address = form.cleaned_data.get(
                    "same_billing_address")
                save_info = form.cleaned_data.get("save_info")
                payment_options = form.cleaned_data.get("payment_options")

                billing_address = Billing_Address(user=self.request.user, street=street,
                                                  apartment=apartment, country=country, zip=zip
                                                  )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                if payment_options == 'S':
                    return redirect("core:payment", payment_option="stripe")
                elif payment_options == 'P':
                    return redirect("core:payment", payment_option="paypal")
                else:
                    messages.error(self.request, "Invalid payment option")
                    return redirect("core:checkout")
            messages.warning(self.request, "Form is not valid")
            return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "Error with your request")
            return redirect("core:orderSummary")


class PaymentView(View):

    def get(self, *args, **kwargs):
        order = Order.objects.get(
            user=self.request.user, ordered=False)

        context = {
            "order": order
        }
        return render(self.request, "payment.html", context)

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amountTotal = int(order.get_total_price() * 100)
        # `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

        try:
            charge = stripe.Charge.create(
                amount=amountTotal,
                currency="usd",
                source=token,
                description="My First Test Charge (created for API docs)",
            )

            payments = Payment()
            payments.user = self.request.user
            payments.stripe_charge_id = charge['id']
            payments.total = order.get_total_price()
            payments.save()

            order.payment = payments
            order.refCode = get_random()

            order.ordered = True

            # updating order items
            for order_item in order.items.all():
                order_item.ordered = True
                order_item.save()

            order.save()

            messages.error(self.request, "Order has been placed successfully")
            return redirect("/")
        # Use Stripe's library to make requests...

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "RateLimitError")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "InvalidRequestError")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "AuthenticationError")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "APIConnectionError")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "StripeError")
            return redirect("/")

        except Exception as e:
            messages.error(
                self.request, "Try again!There wasa problem processing your request at this time")
            # Something else happened, completely unrelated to Stripe
            return redirect("/")


@login_required
def addToCart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = Order_Item.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Added one more of this to your cart!")
            return redirect("core:product", slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, "Added this item to the cart")

            return redirect("core:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, order_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Added this item to the cart")
        return redirect("core:product", slug=slug)


@login_required
def removeFromCart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = Order_Item.objects.get(
                item=item,
                user=request.user,
                ordered=False
            )

            order.items.remove(order_item)
            messages.info(request, "Item removed")
            return redirect("core:product", slug=slug)
        else:
            messages.info(request, "Item does not exist in the current order")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "No active order present")
        return redirect("core:product", slug=slug)


@login_required
def removeOneFromCart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = Order_Item.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity -= 1
            order_item.save()
            if order_item.quantity == 0:
                order.items.remove(order_item)
            messages.info(request, "Removed one more of this from your cart!")
            return redirect("core:orderSummary")

    return redirect("core:orderSummary")


class CouponView(View):

    def get_coupon(code):
        try:
            coupon = Coupon.objects.get(
                code=code)
        except ObjectDoesNotExist:
            messages.error(self.request, "Coupon does not exist")
            return None

    def get(self, *args, **kwargs):
        order = Order.objects.get(
            user=self.request.user, ordered=False)

        context = {
            "order": order
        }
        return render(self.request, "checkout.html", context)

    def post(self, request, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        try:
            order = Order.objects.get(refCode=self.request.user, ordered=False)
            if form.is_valid():
                print(form.cleaned_data)
                code = form.cleaned_data.get("code")
                coupon = Coupon.objects.get(code=code)

                if coupon is None:
                    return redirect("core:checkout")
                else:
                    order.coupon = coupon
                    order.save()
                    return redirect("core:checkout")
            messages.warning(self.request, "Form is not valid")
            return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "Error with your request")
            return redirect("core:orderSummary")


class Refund(View):

    def get(self, *args, **kwargs):
        context = {
            "refundForm": RefundForm()
        }
        return render(self.request, "refundform.html", context)

    def post(self, request, *args, **kwargs):
        form = RefundForm(self.request.POST or None)
        try:
            if form.is_valid():
                print(form.cleaned_data)
                refCode = form.cleaned_data.get("refCode")
                email = form.cleaned_data.get("email")
                comments = form.cleaned_data.get("comments")

                order = Order.objects.get(refCode=refCode)
                order.refund_requested = True
                order.save()
                messages.info(self.request, "Refund request has been filed")
                return redirect("/")
            else:
                messages.warning(self.request, "Form is not valid")
                return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "Error with your request")
            return redirect("/")
