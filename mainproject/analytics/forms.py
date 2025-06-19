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
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label='Category'
    )

    class Meta:
        model = ProductType
        fields = ['category', 'product_category', 'name']

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        # Show no product categories until a category is chosen
        self.fields['product_category'].queryset = ProductCategory.objects.none()
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['product_category'].queryset = ProductCategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.product_category:
            self.fields['product_category'].queryset = ProductCategory.objects.filter(category=self.instance.product_category.category)
            self.fields['category'].initial = self.instance.product_category.category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_type', 'name', 'description', 'image', 'attachment', 'video']

class SubproductForm(forms.ModelForm):
    class Meta:
        model = Subproduct
        fields = ['product', 'name', 'description', 'unit', 'color', 'size']  # added color and size

    def clean_unit(self):
        unit = self.cleaned_data.get('unit')
        if unit is not None and unit < 0:
            raise ValidationError("Unit must not be negative.")
        return unit
