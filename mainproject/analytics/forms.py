from django import forms
from products.models import Category, ProductCategory, ProductType, Product, Subproduct
from django.core.exceptions import ValidationError


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError("This category already exists.")
        return name


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['category', 'name']

class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ['product_category', 'name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_type', 'name', 'description', 'image', 'attachment', 'video']

class SubproductForm(forms.ModelForm):
    class Meta:
        model = Subproduct
        fields = ['product', 'name', 'description', 'unit']


