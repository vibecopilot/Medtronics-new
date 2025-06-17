from django.db import models
from accounts.models import User

# Create your models here.
class EmailLog(models.Model):
    STATUS_CHOICES = [
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
    ]

    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Sent')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email to {self.to_email} on {self.date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-date']
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"