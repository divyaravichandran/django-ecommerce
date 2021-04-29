from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class CheckoutForm(forms.Form):
    street = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': '1234 Main Street'}))
    apartment = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Apt #7'}))
    country = CountryField(blank_label='(Select country)').formfield(
        widget=CountrySelectWidget(
            attrs={'class': 'custom-select d-block w-100'})
    )
    zip = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    same_billing_address = forms.BooleanField(
        required=False, widget=forms.CheckboxInput())
    save_info = forms.BooleanField(
        required=False, widget=forms.CheckboxInput())
    payment_options = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Promo code', 'aria-label': 'Recipient\'s username',
               'aria-describedby': 'basic-addon2'}
    ))


class RefundForm(forms.Form):
    refCode = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'reference code'}))
    email = forms.EmailField()
    comments = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'why am I filing the refund request?'}))
