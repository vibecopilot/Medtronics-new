from django.contrib.auth import  login ,logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm, LoginForm
from .models import User , UserActivity
from django.utils import timezone


def send_login_email(user):
    if not user.email:      
        return
    send_mail(
        subject="Login Alert – Medtronic Portal",
        message=(
            f"Hello {user.username},\n\n"
            f"We noticed a login to your Medtronic account on "
            f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}.\n"   # 👈 timezone‑aware
            "If this was you, no action is needed.\n"
            "If this wasn't you, please change your password immediately.\n\n"
            "Stay secure,\n— The Medtronic Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )

def login_view(request):
    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            if user.role == "user":
                messages.error(request, 'N "Access denied: You do not have permission to log in here.')
                return redirect('home')
            login(request, user)
            now = timezone.now()
            activity = UserActivity.objects.create(
                user=user,
                login_date=now.date(),
                start_time=now.time()
            )
            request.session["activity_id"] = activity.pk
            send_login_email(user)
            messages.success(request, f"Login successful. Welcome, {user.username}!")
            return redirect(reverse_lazy("home"))
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, 'accounts/login.html', {'form': form})





def logout_view(request):
    print('hey i am here')
    activity_id = request.session.pop("activity_id", None)
    if activity_id:
        UserActivity.objects.filter(pk=activity_id, end_time__isnull=True).update(
            end_time=timezone.now(), logout_date=timezone.now().date()
        )
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect(reverse_lazy("login"))


def send_registration_emails(new_user, password):

    user_msg = (
        f"Hi {new_user.username},\n\n"
        f"Welcome aboard! Your Medtronic account has been created successfully.\n\n"
        f"Here are your login credentials:\n"
        f"Username: {new_user.username}\n"
        f"Password: {password}\n\n"
        f"{'You have been registered as an Admin.' if new_user.role == 'admin' else 'You have been registered as a User.'}\n\n"
        f"Please log in and change your password after first login for security.\n\n"
        f"— The Medtronic Team"
    )
    send_mail(
        subject="Welcome to Medtronic!",
        message=user_msg,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[new_user.email],
        fail_silently=True,
    )

    # # Email to all admins
    # admin_emails = User.objects.filter(role='admin').exclude(id=new_user.id).values_list('email', flat=True)
    # if admin_emails:
    #     admin_msg = (
    #         f"Hello Admin,\n\n"
    #         f"A new user has been registered:\n\n"
    #         f"Username: {new_user.username}\n"
    #         f"Role: {new_user.role}\n"
    #         f"You can review user access in the admin panel.\n\n"
    #         f"— Medtronic Security Notification"
    #     )
    #     send_mail(
    #         subject="New User Created – Medtronic Portal",
    #         message=admin_msg,
    #         from_email=settings.DEFAULT_FROM_EMAIL,
    #         recipient_list=list(admin_emails),
    #         fail_silently=True,
    #     )

# @login_required
def register_view(request):
    # if request.user.role != 'admin':
    #     messages.error(request, "You are not authorized to access the registration page.")
    #     return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            password = form.cleaned_data['password1']
            new_user = form.save(commit=False)
            new_user.set_password(password)
            # Set role based on who is creating the account
            if request.user.is_authenticated:
                if request.user.role == 'admin':
                    new_user.role = 'admin'
                else:
                     new_user.role = 'user'
            else:
                new_user.role = 'user'

            new_user.save()
            send_registration_emails(new_user, password)
            messages.success(request, f"User '{new_user.username}' created and notified successfully.")
            if request.user.is_authenticated:
                return redirect('home')
            else:
                return redirect('login')
        else:
            messages.error(request,form.errors)
            messages.error(request, "Please correct the errors below.")
    
    return render(request, 'accounts/register.html', {'form': form})

