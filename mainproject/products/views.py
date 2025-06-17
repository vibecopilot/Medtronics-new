from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Prefetch
from .models import Category, ProductCategory, ProductType, Product
from django.contrib.auth.decorators import login_required

def category_view(request):
    """Optimized category view with prefetch_related for better performance"""
    categories = Category.objects.prefetch_related(
        Prefetch('product_categories', queryset=ProductCategory.objects.select_related())
    )
    return render(request, 'products/category_list.html', {'categories': categories})

from .models import Product, OrderProductOnline
from .forms import OrderProductOnlineForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

@login_required
def order_product_online_view(request, product_id):
    if request.user.role == 'admin':
        messages.error(request, "Admins are not allowed to order products.")
        return redirect('product_detail', pk=product_id)
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = OrderProductOnlineForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.product = product
            order.save()

            # Prepare mail details
            subject = f"Order Placed: {product.name}"
            user_message = (
                f"Dear {request.user.get_full_name() or request.user.username},\n\n"
                f"Your order for '{product.name}' has been placed successfully!\n"
                f"Order details:\n"
                f"Region: {order.region}\n"
                f"Name: {order.name}\n"
                f"Address: {order.address}\n"
                f"Contact Number: {order.number}\n\n"
                f"Thank you for ordering with us."
            )
            admin_message = (
                f"New product order placed by {request.user.get_full_name() or request.user.username} ({request.user.email}):\n\n"
                f"Product: {product.name}\n"
                f"Region: {order.region}\n"
                f"Name: {order.name}\n"
                f"Address: {order.address}\n"
                f"Contact Number: {order.number}\n"
            )

            # Send mail to user
            send_mail(
                subject,
                user_message,
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
            )

            # Send mail to all admins
            User = get_user_model()
            admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
            if admin_emails:
                send_mail(
                    subject,
                    admin_message,
                    settings.EMAIL_HOST_USER,
                    list(admin_emails),
                    fail_silently=False,
                )

            messages.success(request, "Your order has been placed successfully!")
            return redirect('product_detail', pk=product_id)
    else:
        form = OrderProductOnlineForm(user=request.user)
    return render(request, 'products/order_form.html', {
        'form': form,
        'product': product,
    })



def product_category_view(request, pk):
    """Optimized product category view with better query optimization"""
    # Get product category with select_related for better performance
    product_category = get_object_or_404(
        ProductCategory.objects.select_related('category'), 
        pk=pk
    )
    catname=product_category.category.name
    # Get product types for this category
    product_types = ProductType.objects.filter(
        product_category=product_category
    ).order_by('name')
    # Get filter parameters
    selected_types = request.GET.getlist('product_type')
    search_query = request.GET.get('search', '').strip()
    
    # Build optimized queryset with select_related and prefetch_related
    products = Product.objects.select_related(
        'product_type', 
        'product_type__product_category'
    ).filter(
        product_type__product_category=product_category
    )
    
    # Apply filters
    if selected_types:
        # Convert to integers and filter out invalid values
        try:
            selected_type_ids = [int(t) for t in selected_types if t.isdigit()]
            if selected_type_ids:
                products = products.filter(product_type__id__in=selected_type_ids)
        except ValueError:
            pass  # Invalid type IDs, ignore filter
    
    # Apply search filter with case-insensitive search on multiple fields
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Order products for consistent pagination
    products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Convert selected_types to integers for template comparison
    selected_types_int = []
    for t in selected_types:
        try:
            selected_types_int.append(int(t))
        except (ValueError, TypeError):
            pass
    print('mai idher hu',product_category)
    return render(request, 'products/product_list.html', {
        'product_category': product_category,
        'product_types': product_types,
        'products': page_obj,
        'selected_types': selected_types_int,
        'search_query': search_query,
        'productskey':catname
    })


def product_detail_view(request, pk):
    """Optimized product detail view with better related products logic"""
    # Get product with related data
    product = get_object_or_404(
        Product.objects.select_related(
            'product_type', 
            'product_type__product_category'
        ), 
        pk=pk
    )
    
    # Intelligent related product logic with multiple fallback strategies
    related_products = None
    
    # Strategy 1: Same product type, exclude current product
    related_products = Product.objects.select_related('product_type').filter(
        product_type=product.product_type
    ).exclude(pk=product.pk)[:4]
    
    # Strategy 2: If not enough products, get from same category
    if related_products.count() < 4:
        additional_products = Product.objects.select_related('product_type').filter(
            product_type__product_category=product.product_type.product_category
        ).exclude(
            pk=product.pk
        ).exclude(
            pk__in=[p.pk for p in related_products]
        )[:4 - related_products.count()]
        
        # Combine querysets
        related_products = list(related_products) + list(additional_products)
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'productname':product.name
    })




from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect
from .models import Product, Wishlist
from django.contrib import messages

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist_qs = Wishlist.objects.filter(user=request.user, product=product)
    if wishlist_qs.exists():
        wishlist_qs.delete()
        messages.success(request, "Product Removed from your Wishlist.")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, "Successfully added to your Wishlist.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user, is_active=True)
    
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, product_id):
    if request.method == "POST":
        wishlist_item = Wishlist.objects.filter(user=request.user, product_id=product_id)
        if wishlist_item.exists():
            wishlist_item.delete()
            messages.success(request, "Product removed from your wishlist.")
    return redirect('wishlist_view')




@login_required
def store_searched_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        if not product_id:
            messages.error(request, 'No product selected.')

            return redirect(request.META.get('HTTP_REFERER', 'product_list'))

        try:
            product = Product.objects.select_related(
                'product_type',
                'product_type__product_category'
            ).get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Product not found.')
            return redirect(request.META.get('HTTP_REFERER', 'product_list'))

        SearchProduct.objects.create(user=request.user, product=product)

        related_products = Product.objects.select_related('product_type').filter(
            product_type=product.product_type
        ).exclude(pk=product.pk)[:4]

        if related_products.count() < 4:
            additional_products = Product.objects.select_related('product_type').filter(
                product_type__product_category=product.product_type.product_category
            ).exclude(
                pk=product.pk
            ).exclude(
                pk__in=[p.pk for p in related_products]
            )[:4 - related_products.count()]
            related_products = list(related_products) + list(additional_products)

        return render(request, 'products/product_detail.html', {
            'product': product,
            'related_products': related_products
        })

    messages.error(request, 'Invalid request method.')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))