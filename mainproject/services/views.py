from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import DemoForm, TrainingForm, ProductForm
from products.models import Product, Category ,ProductCategory,ProductType
from accounts.models import User
from services.models import RequestLog, RequestType

def build_admin_message(form):
    info = [
        f"Name: {form.cleaned_data.get('name', '')}",
        f"Email: {form.cleaned_data.get('email', '')}",
        f"Contact Number: {form.cleaned_data.get('contact_number', '')}",
        f"Address: {form.cleaned_data.get('address', '')}",
    ]

    # For each, if it is int or str (an id), fetch the object; if already object, get name.
    category = form.cleaned_data.get('category')
    if category:
        if isinstance(category, (int, str)):  # If it's an ID
            try:
                category_obj = Category.objects.get(pk=category)
                info.append(f"Category: {category_obj.name}")
            except Category.DoesNotExist:
                info.append(f"Category: Unknown")
        else:
            info.append(f"Category: {getattr(category, 'name', str(category))}")

    product_category = form.cleaned_data.get('product_category')
    if product_category:
        if isinstance(product_category, (int, str)):
            try:
                pc_obj = ProductCategory.objects.get(pk=product_category)
                info.append(f"Product Category: {pc_obj.name}")
            except ProductCategory.DoesNotExist:
                info.append(f"Product Category: Unknown")
        else:
            info.append(f"Product Category: {getattr(product_category, 'name', str(product_category))}")

    product_type = form.cleaned_data.get('product_type')
    if product_type:
        if isinstance(product_type, (int, str)):
            try:
                pt_obj = ProductType.objects.get(pk=product_type)
                info.append(f"Product Type: {pt_obj.name}")
            except ProductType.DoesNotExist:
                info.append(f"Product Type: Unknown")
        else:
            info.append(f"Product Type: {getattr(product_type, 'name', str(product_type))}")

    product = form.cleaned_data.get('product')
    if product:
        if isinstance(product, (int, str)):
            try:
                p_obj = Product.objects.get(pk=product)
                info.append(f"Product: {p_obj.name}")
            except Product.DoesNotExist:
                info.append(f"Product: Unknown")
        else:
            info.append(f"Product: {getattr(product, 'name', str(product))}")

    return "Dear Admin,\n\nA new request has been submitted with the following details:\n\n" + "\n".join(info)


def demo_request_view(request):
    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin':
        messages.error(request, "Admins cannot access this form.")
        return redirect('home')
    categories = Category.objects.all()
    form = DemoForm(request.POST or None, user=getattr(request, 'user', None))
    if request.method == 'POST':
        if form.is_valid():
            demo_request_type = RequestType.objects.get(name="Demo")
            product = form.cleaned_data['product']
            product_type = product.product_type
            product_category = product_type.product_category
            category = product_category.category

            RequestLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                product=product,
                product_type=product_type,
                product_category=product_category,
                category=category,
                request_type=demo_request_type,
                name=form.cleaned_data['name'],
                address=form.cleaned_data['address'],
                number=form.cleaned_data['contact_number']
            )
            subject = "New Demo Request Submitted"
            # User email
            message = (
                f"Dear {form.cleaned_data['name']},\n\n"
                f"Your demo request has been submitted successfully.\n\n"
                f"Product: {product}\n"
                f"Address: {form.cleaned_data['address']}\n"
                f"Phone Number: {form.cleaned_data['contact_number']}\n"
            )
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [form.cleaned_data['email']],
                fail_silently=False,
            )
            # Admin email
            admin_emails = User.objects.filter(role='admin').values_list('email', flat=True)
            admin_message = build_admin_message(form)
            if admin_emails:
                send_mail(
                    subject,
                    admin_message,
                    settings.EMAIL_HOST_USER,
                    list(admin_emails),
                    fail_silently=False,
                )
            messages.success(request, "Your demo request has been submitted successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'services/demoform.html', {'form': form, 'categories': categories})


def training_request_view(request):
    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin':
        messages.error(request, "Admins cannot access this form.")
        return redirect('home')
    categories = Category.objects.all()
    form = TrainingForm(request.POST or None, user=getattr(request, 'user', None))
    if request.method == 'POST':
        if form.is_valid():
            training_request_type = RequestType.objects.get(name="Training")
            product = form.cleaned_data['product']
            product_type = product.product_type
            product_category = product_type.product_category
            category = product_category.category

            RequestLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                product=product,
                product_type=product_type,
                product_category=product_category,
                category=category,
                request_type=training_request_type,
                name=form.cleaned_data['name'],
                address=form.cleaned_data['address'],
                number=form.cleaned_data['contact_number']
            )
            subject = "New Training Request Submitted"
            # User email
            message = (
                f"Dear {form.cleaned_data['name']},\n\n"
                f"Your training request has been submitted successfully.\n\n"
                f"Product: {product}\n"
                f"Address: {form.cleaned_data['address']}\n"
                f"Phone Number: {form.cleaned_data['contact_number']}\n"
            )
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [form.cleaned_data['email']],
                fail_silently=False,
            )
            # Admin email
            admin_emails = User.objects.filter(role='admin').values_list('email', flat=True)
            admin_message = build_admin_message(form)
            if admin_emails:
                send_mail(
                    subject,
                    admin_message,
                    settings.EMAIL_HOST_USER,
                    list(admin_emails),
                    fail_silently=False,
                )
            messages.success(request, "Your training request has been submitted successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'services/trainingform.html', {'form': form, 'categories': categories})


def product_request_view(request):
    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin':
        messages.error(request, "Admins cannot access this form.")
        return redirect('home')
    categories = Category.objects.all()
    form = ProductForm(request.POST or None, user=getattr(request, 'user', None))
    if request.method == 'POST':
        if form.is_valid():
            product_request_type = RequestType.objects.get(name="Product")
            product = form.cleaned_data['product']
            product_type = product.product_type
            product_category = product_type.product_category
            category = product_category.category

            RequestLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                product=product,
                product_type=product_type,
                product_category=product_category,
                category=category,
                request_type=product_request_type,
                name=form.cleaned_data['name'],
                address=form.cleaned_data['address'],
                number=form.cleaned_data['contact_number']
            )
            subject = "New Product Request Submitted"
            # User email
            message = (
                f"Dear {form.cleaned_data['name']},\n\n"
                f"Your product request has been submitted successfully.\n\n"
                f"Product: {product}\n"
                f"Address: {form.cleaned_data['address']}\n"
                f"Phone Number: {form.cleaned_data['contact_number']}\n"
            )
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [form.cleaned_data['email']],
                fail_silently=False,
            )
            admin_emails = User.objects.filter(role='admin').values_list('email', flat=True)
            admin_message = build_admin_message(form)
            if admin_emails:
                send_mail(
                    subject,
                    admin_message,
                    settings.EMAIL_HOST_USER,
                    list(admin_emails),
                    fail_silently=False,
                )
            messages.success(request, "Your product request has been submitted successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'services/productform.html', {'form': form, 'categories': categories})

def thank_you_view(request):
    pass