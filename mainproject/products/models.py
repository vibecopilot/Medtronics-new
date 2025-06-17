from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import User
from django.core.validators import FileExtensionValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product_categories")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"



class ProductType(models.Model):
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="product_types")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.product_category.name})"


class Product(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    attachment = models.FileField(
        upload_to='product_files/attachments/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'webp'])],
        help_text="Upload PDF, Word, or Image file"
    )

    video = models.FileField(
        upload_to='product_files/videos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv'])],
        help_text="Upload video file (e.g., .mp4, .mov)"
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.product_type.name})"


class Subproduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="subproducts")
    name = models.CharField(max_length=100)
    description = models.TextField()
    unit = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.product.name})"


class Region(models.Model):
    country_code = models.CharField(max_length=2, unique=True)
    country_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("country_name",)

    def __str__(self):
        return self.country_name


class OrderProductOnline(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"

    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="orders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    name = models.CharField(max_length=100, help_text="Person requesting")
    address = models.TextField(help_text="Full address of requester")
    number = models.CharField(max_length=15, help_text="Contact number")
    order_date = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f"Order #{self.pk} | {self.user} → {self.product.name} ({self.get_status_display()})"


class SearchProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} searched {self.product.name} on {self.date.strftime('%Y-%m-%d %H:%M')}"
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'

    def __str__(self):
        return f"{self.user.username} → {self.product.name}"

class AttachmentDownloadLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='downloads')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.product.name}  - {self.downloaded_at}"