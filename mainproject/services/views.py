from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DemoForm, TrainingForm, ProductForm
from .models import RequestLog, RequestType
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
# Demo form view
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import DemoForm, TrainingForm
from products.models import Product, Category
from accounts.models import User
from services.models import RequestLog, RequestType

@login_required
def demo_form_view(request):
    if request.user.role == 'admin':
        messages.error(request, "Admins cannot access this form.")
        return redirect('home')
    form = DemoForm(request.POST or None, user=request.user)
    if form.is_valid():
        demo_request_type = RequestType.objects.get(name="Demo")
        RequestLog.objects.create(
            user=request.user,
            product=form.cleaned_data['product'],
            request_type=demo_request_type,
            name=form.cleaned_data['name'],
            address=form.cleaned_data['address'],
            number=form.cleaned_data['contact_number']
        )
        # Prepare email subject and body
        subject = "New Demo Request Submitted"
        message = (
            f"Dear {form.cleaned_data['name']},\n\n"
            f"Your demo request has been submitted successfully.\n\n"
            f"Product: {form.cleaned_data['product']}\n"
            f"Address: {form.cleaned_data['address']}"
        )
        # Send email to the user
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [form.cleaned_data['email']],
            fail_silently=False,
        )
        # Send email to all admin users
        admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
        if admin_emails:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                admin_emails,
                fail_silently=False,
            )
        messages.success(request, "Your demo request has been submitted successfully!")
        return redirect('thank_you')
    return render(request, 'services/demoform.html', {'form': form})

@login_required
def training_form_view(request):
    if request.user.role == 'admin':
        messages.error(request, "Admins cannot access this form.")
        return redirect('home')
    form = TrainingForm(request.POST or None, user=request.user)
    if form.is_valid():
        training_request_type = RequestType.objects.get(name="Training")
        RequestLog.objects.create(
            user=request.user,
            product=form.cleaned_data['product'],
            request_type=training_request_type,
            name=form.cleaned_data['name'],
            address=form.cleaned_data['address'],
            number=form.cleaned_data['contact_number']
        )
        # Prepare email subject and body
        subject = "New Training Request Submitted"
        message = (
            f"Dear {form.cleaned_data['name']},\n\n"
            f"Your training request has been submitted successfully.\n\n"
            f"Product: {form.cleaned_data['product']}\n"
            f"Address: {form.cleaned_data['address']}"
        )
        # Send email to the user
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [form.cleaned_data['email']],
            fail_silently=False,
        )
        # Send email to all admin users
        admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
        if admin_emails:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                admin_emails,
                fail_silently=False,
            )
        messages.success(request, "Your training request has been submitted successfully!")
        return redirect('thank_you')
    return render(request, 'services/trainingform.html', {'form': form})


# Product form view
@login_required
def product_form_view(request):
    if request.user.role == 'admin':
        messages.error(request, "Admins cannot access this form.")
        return redirect('home')

    form = ProductForm(request.POST or None, user=request.user)
    if form.is_valid():
        product_request_type = RequestType.objects.get(name="Product")
        RequestLog.objects.create(
            user=request.user,
            product=form.cleaned_data['product'],
            request_type=product_request_type,
            name=form.cleaned_data['name'],
            address=form.cleaned_data['address'],
            number=form.cleaned_data['contact_number']
        )

        # Prepare email subject and body
        subject = "New Product Request Submitted"
        message = f"Dear {form.cleaned_data['name']},\n\nYour product request has been submitted successfully.\n\nProduct: {form.cleaned_data['product']}\nAddress: {form.cleaned_data['address']}"

        # Send email to the user
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [request.user.email],  # Send to the user's email
            fail_silently=False,
        )

        # Send email to all admin users
        admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
        if admin_emails:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                admin_emails,  # Send to all admin emails
                fail_silently=False,
            )

        # Success message
        messages.success(request, "Your product request has been submitted successfully!")
        return redirect('thank_you')  # Redirect to a thank you page or somewhere else

    return render(request, 'services/productform.html', {'form': form})






from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import RequestLog, RequestType
from .forms import DemoForm, TrainingForm, ProductForm

def demo_request_view(request):
    form = DemoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        # Create the request log for demo request
        demo_request_type = RequestType.objects.get(name="Demo")
        RequestLog.objects.create(
            user=request.user,
            product=form.cleaned_data['product'],
            request_type=demo_request_type,
            name=form.cleaned_data['name'],
            address=form.cleaned_data['address'],
            number=form.cleaned_data['contact_number']
        )
        return HttpResponseRedirect('/thank-you/')  # Redirect to a thank you page or similar
    return render(request, 'services/demoform.html', {'form': form})

def training_request_view(request):
    form = TrainingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        # Create the request log for training request
        training_request_type = RequestType.objects.get(name="Training")
        RequestLog.objects.create(
            user=request.user,
            product=form.cleaned_data['product'],
            request_type=training_request_type,
            name=form.cleaned_data['name'],
            address=form.cleaned_data['address'],
            number=form.cleaned_data['contact_number']
        )
        return HttpResponseRedirect('/thank-you/')
    return render(request, 'services/trainingform.html', {'form': form})

def product_request_view(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        # Create the request log for product request
        product_request_type = RequestType.objects.get(name="Product")
        RequestLog.objects.create(
            user=request.user,
            product=form.cleaned_data['product'],
            request_type=product_request_type,
            name=form.cleaned_data['name'],
            address=form.cleaned_data['address'],
            number=form.cleaned_data['contact_number']
        )
        return HttpResponseRedirect('/thank-you/')
    return render(request, 'services/productform.html', {'form': form})


def request_list_view(request):
    # Optionally, you can filter by request type (e.g., 'Demo', 'Training', 'Product')
    request_logs = RequestLog.objects.all().order_by('-created_at')  # Order by creation date
    return render(request, 'services/list.html', {'request_logs': request_logs})

# views.py
def thank_you_view(request):
    return render(request, 'services/thank_you.html')


