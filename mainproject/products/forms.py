from .models import OrderProductOnline, Region
from django import forms
import re

# forms.py

class OrderProductOnlineForm(forms.ModelForm):
    class Meta:
        model = OrderProductOnline
        fields = ['region', 'name', 'address', 'number']
        widgets = {
            'region': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '10-digit mobile or phone number'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            # Set initial values. Adjust as per your User model.
            self.fields['name'].initial = user.get_full_name() or user.username
            # If you have address/number in user profile, fill them too.
            if hasattr(user, 'profile'):  # If you use a profile model
                self.fields['address'].initial = user.profile.address
                self.fields['number'].initial = user.profile.contact_number
            # Otherwise, skip or customize as per your setup.

    # (Keep your clean_* methods as-is)

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
        # Simple validation for Indian mobile/phone numbers (modify if needed)
        if not re.match(r"^\d{10,15}$", number):
            raise forms.ValidationError("Enter a valid contact number (10-15 digits).")
        return number

    def clean_region(self):
        region = self.cleaned_data.get('region')
        if not region:
            raise forms.ValidationError("Please select a region.")
        return region