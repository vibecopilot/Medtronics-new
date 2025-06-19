from .models import OrderProductOnline, Region
from django import forms
import re

# forms.py
class OrderProductOnlineForm(forms.ModelForm):
    class Meta:
        model = OrderProductOnline
        fields = ['region', 'name', 'email', 'address', 'number']   # <-- include 'email'
        widgets = {
            'region': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '10-digit mobile or phone number'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email
            # Optional: autofill address, number from profile
            if hasattr(user, 'profile'):
                self.fields['address'].initial = user.profile.address
                self.fields['number'].initial = user.profile.contact_number

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        if not re.match(r"^[A-Za-z\s.]+$", name):
            raise forms.ValidationError("Name must contain only letters, spaces, or periods.")
        return name

    def clean_address(self):
        address = self.cleaned_data.get('address', '').strip()
        if not address:
            raise forms.ValidationError("Address is required.")
        if len(address) < 10:
            raise forms.ValidationError("Address is too short.")
        return address

    def clean_number(self):
        number = self.cleaned_data.get('number', '').strip()
        if not number:
            raise forms.ValidationError("Contact number is required.")
        if not re.match(r"^\d{10,15}$", number):
            raise forms.ValidationError("Enter a valid contact number (10-15 digits).")
        return number

    def clean_region(self):
        region = self.cleaned_data.get('region')
        if not region:
            raise forms.ValidationError("Please select a region.")
        return region

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError("Email is required.")
        # Django's EmailField already validates format.
        return email
