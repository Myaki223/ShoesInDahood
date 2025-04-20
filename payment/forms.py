from django import forms
from .models import ShippingAddress

class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'shipping_full_name',
            'shipping_email',
            'shipping_address1',
            'shipping_address2',
            'shipping_city',
            'shipping_state',
            'shipping_zipcode',
            'shipping_country',
            'phone_number',
        ]

        widgets = {
            'shipping_full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'shipping_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'shipping_address1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address1'}),
            'shipping_address2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address2'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'shipping_state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'shipping_zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zipcode'}),
            'shipping_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
        }

class PaymentsForm(forms.Form):
    card_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Name on Card'}), required=True)
    card_number = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Card Number'}), required=True)
    card_exp_date = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Expiration Date'}), required=True)
    card_cvv_number = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'CVV Code'}), required=True)
    card_address1 =forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Billing Address 1 '}), required=True)
    card_address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Billing Address 1 '}), required=True)
    card_city = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Billing City'}), required=True)
    card_state = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Billing State'}), required=True)
    card_zipcode =forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Billing Zipcode'}), required=True)
    card_country = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Billing Country'}), required=True)