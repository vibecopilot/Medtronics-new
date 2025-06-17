from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['username']


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    logout_date = models.DateField(null=True, blank=True)

    @property
    def session_duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def __str__(self):
        return f"{self.user.username} session on {self.login_date}"

    class Meta:
        ordering = ['-login_date', '-start_time']
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"