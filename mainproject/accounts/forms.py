from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.core.exceptions import ValidationError
import re
from .models import User

class LoginForm(AuthenticationForm):
    """Simple username / password login form with Bootstrap‑friendly widgets."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username",
        }),
        label="",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
        }),
        label="",
    )



User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(
        required=True,
        max_length=30,
        label="First Name",
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
    )
    last_name = forms.CharField(
        required=True,
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and ./-/_ characters.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[A-Za-z\s-]+$', first_name):
            raise ValidationError("First name must only contain letters, spaces, or hyphens.")
        if len(first_name) < 2:
            raise ValidationError("First name must be at least 2 characters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[A-Za-z\s-]+$', last_name):
            raise ValidationError("Last name must only contain letters, spaces, or hyphens.")
        if len(last_name) < 2:
            raise ValidationError("Last name must be at least 2 characters.")
        return last_name



