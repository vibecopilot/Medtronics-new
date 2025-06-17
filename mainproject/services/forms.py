from django import forms
from django.core.exceptions import ValidationError
from products.models import Product, Category
import re

# Custom validators
def validate_name(value):
    if not value.replace(" ", "").isalpha():
        raise ValidationError('Name must contain only alphabets and spaces.')

def validate_contact_number(value):
    if not value.isdigit():
        raise ValidationError('Contact number must contain only digits.')
    if len(value) != 10:
        raise ValidationError('Contact number must be 10 digits long.')

def validate_address(value):
    if len(value.strip()) < 10:
        raise ValidationError('Address must be at least 10 characters long.')

def validate_email(value):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        raise ValidationError('Enter a valid email address.')

class DemoForm(forms.Form):
    name = forms.CharField(max_length=255, validators=[validate_name])
    email = forms.EmailField(validators=[validate_email])
    contact_number = forms.CharField(max_length=15, validators=[validate_contact_number])
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    address = forms.CharField(widget=forms.Textarea, validators=[validate_address])

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email

class TrainingForm(forms.Form):
    name = forms.CharField(max_length=255, validators=[validate_name])
    email = forms.EmailField(validators=[validate_email])
    contact_number = forms.CharField(max_length=15, validators=[validate_contact_number])
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    address = forms.CharField(widget=forms.Textarea, validators=[validate_address])

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email
# Pre-fill name with user's full name

class ProductForm(forms.Form):
    name = forms.CharField(max_length=255, validators=[validate_name])
    email = forms.EmailField(validators=[validate_email])
    contact_number = forms.CharField(max_length=15, validators=[validate_contact_number])
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    address = forms.CharField(widget=forms.Textarea, validators=[validate_address])

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email
