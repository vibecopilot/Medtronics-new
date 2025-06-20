from django import forms
from django.core.exceptions import ValidationError
from products.models import Product, Category
import re

# --- Custom validators ---
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

# --- AJAX-ready Base Form ---
class AjaxProductRequestForm(forms.Form):
    name = forms.CharField(max_length=255, validators=[validate_name])
    email = forms.EmailField(validators=[validate_email])
    contact_number = forms.CharField(max_length=15, validators=[validate_contact_number])
    # Remove queryset here!
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=True)
    product_category = forms.CharField(required=False)
    product_type = forms.CharField(required=False)
    product = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea, validators=[validate_address])

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Set the queryset dynamically here!
        self.fields['category'].queryset = Category.objects.filter(is_avaliable=True)
        if user and getattr(user, 'is_authenticated', False):
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email

    def clean_product(self):
        product_id = self.cleaned_data.get('product')
        if not product_id or not str(product_id).isdigit():
            raise ValidationError("Please select a valid Product.")
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise ValidationError("Selected Product does not exist.")
        return product




    # You can add similar clean_product_category and clean_product_type if you want to enforce validation

# --- Inherit for specific forms ---
class DemoForm(AjaxProductRequestForm):
    pass

class TrainingForm(AjaxProductRequestForm):
    pass

class ProductForm(AjaxProductRequestForm):
    pass