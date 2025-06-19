from .models import (
    Product, OrderProductOnline, Wishlist,
    Category, ProductCategory, ProductType
)
from .forms import OrderProductOnlineForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from products.models import SearchProduct
from django.http import JsonResponse

def category_view(request):
    """Optimized category view showing only available categories and their products"""

    categories = Category.objects.filter(is_avaliable=True).prefetch_related(
        Prefetch(
            'product_categories',
            queryset=ProductCategory.objects.select_related().order_by('name')
        )
    ).order_by('name')

    all_products = Product.objects.filter(
    product_type__product_category__category__is_avaliable=True
)
    return render(request, 'products/category_list.html', {'categories': categories,'all_products':all_products})

def order_product_online_view(request, product_id):
    # Restrict admin
    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin':
        messages.error(request, "Admins are not allowed to order products.")
        return redirect('product_detail', pk=product_id)

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = OrderProductOnlineForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.product = product
            order.save()

            # Prepare mail details (ALWAYS use the form's data!)
            subject = f"Order Placed: {product.name}"
            user_message = (
                f"Dear {order.name},\n\n"
                f"Your order for '{product.name}' has been placed successfully!\n"
                f"Order details:\n"
                f"Region: {order.region}\n"
                f"Name: {order.name}\n"
                f"Address: {order.address}\n"
                f"Contact Number: {order.number}\n\n"
                f"Thank you for ordering with us."
            )
            admin_message = (
                f"New product order placed by {order.name} ({order.email}):\n\n"
                f"Product: {product.name}\n"
                f"Region: {order.region}\n"
                f"Name: {order.name}\n"
                f"Address: {order.address}\n"
                f"Contact Number: {order.number}\n"
            )

            # Send mail to user (form's email)
            send_mail(
                subject,
                user_message,
                settings.EMAIL_HOST_USER,
                [order.email],  # << always use form email!
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
    product_category = get_object_or_404(
        ProductCategory.objects.select_related('category'),
        pk=pk
    )
    catname = product_category.category.name

    product_types = ProductType.objects.filter(
        product_category=product_category
    ).order_by('name')

    selected_types = request.GET.getlist('product_type')
    search_query = request.GET.get('search', '').strip()

    products = Product.objects.select_related(
        'product_type', 'product_type__product_category'
    ).filter(
        product_type__product_category=product_category,
        product_type__product_category__category__is_avaliable=True

    )

    selected_types_int = []
    for t in selected_types:
        try:
            tid = int(t)
            selected_types_int.append(tid)
        except (ValueError, TypeError):
            pass

    if selected_types_int:
        products = products.filter(product_type__id__in=selected_types_int)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    products = products.order_by('name')

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_products = Product.objects.filter(
        product_type__product_category=product_category
    ).values('pk', 'name', 'image')

    return render(request, 'products/product_list.html', {
        'product_category': product_category,
        'product_types': product_types,
        'products': page_obj,
        'selected_types': selected_types_int,
        'search_query': search_query,
        'productskey': catname,
        'all_products': all_products,
    })

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

        # No @login_required, so check user before using
        if request.user.is_authenticated:
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

def product_detail_view(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('product_type', 'product_type__product_category'),
        pk=pk
    )
    wishlisted = False
    if request.user.is_authenticated:
        wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()

    # Get related subproducts of the current product
    related_subproducts = Subproduct.objects.filter(product=product)

    has_color = related_subproducts.first().color if related_subproducts.exists() else False
    has_size = related_subproducts.first().size if related_subproducts.exists() else False
    print(related_subproducts)
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_subproducts': related_subproducts,
        'productname': product.name,
        'wishlisted': wishlisted,
        'has_color': bool(has_color),
        'has_size': bool(has_size),
    })



def toggle_wishlist(request, product_id):
    # No @login_required; check if logged in!
    if not request.user.is_authenticated:
        messages.error(request, "Please login to use the wishlist.")
        return redirect('login')

    product = get_object_or_404(Product, pk=product_id)
    wishlist_qs = Wishlist.objects.filter(user=request.user, product=product)
    if wishlist_qs.exists():
        wishlist_qs.delete()
        messages.success(request, "Product Removed from your Wishlist.")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, "Successfully added to your Wishlist.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

def wishlist_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to view your wishlist.")
        return redirect('login')
    wishlist_items = Wishlist.objects.filter(user=request.user, is_active=True)
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})

def remove_from_wishlist(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to modify your wishlist.")
        return redirect('login')
    if request.method == "POST":
        wishlist_item = Wishlist.objects.filter(user=request.user, product_id=product_id)
        if wishlist_item.exists():
            wishlist_item.delete()
            messages.success(request, "Product removed from your wishlist.")
    return redirect('wishlist_view')

def ajax_product_categories(request):
    category_id = request.GET.get('category_id')
    product_categories = ProductCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'product_categories': list(product_categories)})

def ajax_product_types(request):
    product_category_id = request.GET.get('product_category_id')
    product_types = ProductType.objects.filter(product_category_id=product_category_id).values('id', 'name')
    return JsonResponse({'product_types': list(product_types)})

def ajax_products(request):
    product_type_id = request.GET.get('product_type_id')
    products = Product.objects.filter(product_type_id=product_type_id).values('id', 'name')
    return JsonResponse({'products': list(products)})





from .models import Subproduct
from django.shortcuts import render, get_object_or_404

def subproduct_detail_view(request, pk):
    subproduct = get_object_or_404(Subproduct, pk=pk)
    product = subproduct.product
    print(f"Subproduct pk: {pk}")
    other_subproducts = Subproduct.objects.filter(product=subproduct.product)
    print(f"Other subproducts count: {other_subproducts.count()}")
    return render(request, 'products/subproduct_detail.html', {
        'subproduct': subproduct,
        'product': product,
        'other_subproducts': other_subproducts,
    })