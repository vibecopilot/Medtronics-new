from django.db import models
from accounts.models import User
from products.models import Product


class RequestType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Request Type"
        verbose_name_plural = "Request Types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class RequestLog(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        COMPLETED = "Completed", "Completed"
        REJECTED = "Rejected", "Rejected"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="requests")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="requests")
    request_type = models.ForeignKey(RequestType, on_delete=models.CASCADE, related_name="logs")
    name = models.CharField(max_length=100, help_text="Person requesting")
    address = models.TextField(help_text="Full address of requester")
    number = models.CharField(max_length=15, help_text="Contact number")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"

    def __str__(self):
        return f"{self.request_type.name} - {self.name} ({self.status})"