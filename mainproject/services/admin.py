from django.contrib import admin
from .models import RequestLog,RequestType
# Register your models here.

admin.site.register([RequestType,RequestLog])