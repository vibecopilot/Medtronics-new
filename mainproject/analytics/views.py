from django.db.models import Count
from django.shortcuts import render,redirect
from products.models import SearchProduct, AttachmentDownloadLog, Product, ProductType, ProductCategory
from services.models import RequestLog  
from datetime import timedelta
from accounts.models import User, UserActivity
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.contrib import messages
from collections import defaultdict
from products.models import *
from .forms import *


def check_admin_permission(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, "Access denied: Admins only.")
        return False
    return True


def vendor_list_view(request):
    if not check_admin_permission(request):
        return redirect('home')  
    vendors = User.objects.filter(role='user')
    return render(request, 'analytics/list.html', {'title': 'All Vendors', 'vendors': vendors})

def active_vendors_view(request):
    if not check_admin_permission(request):
        return redirect('home')  
    recent_date = now() - timedelta(days=30)
    vendor_ids = UserActivity.objects.filter(login_date__gte=recent_date, user__role='user').values_list('user', flat=True).distinct()
    vendors = User.objects.filter(id__in=vendor_ids)
    return render(request, 'analytics/list.html', {'title': 'Active Vendors (Last 30 Days)', 'vendors': vendors})

def logged_in_vendors_view(request):
    if not check_admin_permission(request):
        return redirect('home')  
    vendor_ids = UserActivity.objects.filter(user__role='user').values_list('user', flat=True).distinct()
    vendors = User.objects.filter(id__in=vendor_ids)
    return render(request, 'analytics/list.html', {'title': 'Vendors Logged In At Least Once', 'vendors': vendors})

def new_vendors_week_view(request):
    if not check_admin_permission(request):
        return redirect('home')
    start_of_week = now() - timedelta(days=now().weekday())
    vendors = User.objects.filter(role='user', date_joined__gte=start_of_week)
    return render(request, 'analytics/list.html', {'title': 'New Vendors This Week', 'vendors': vendors})

def new_vendors_month_view(request):
    if not check_admin_permission(request):
        return redirect('home')
    start_of_month = now().replace(day=1)
    vendors = User.objects.filter(role='user', date_joined__gte=start_of_month)
    return render(request, 'analytics/list.html', {'title': 'New Vendors This Month', 'vendors': vendors})

def dau_view(request):
    if not check_admin_permission(request):
        return redirect('home')
    today = now().date()
    vendor_ids = UserActivity.objects.filter(login_date=today, user__role='user').values_list('user', flat=True).distinct()
    vendors = User.objects.filter(id__in=vendor_ids)
    return render(request, 'analytics/list.html', {'title': 'Daily Active Vendors (Today)', 'vendors': vendors})

def wau_view(request):
    if not check_admin_permission(request):
        return redirect('home')
    start_of_week = now() - timedelta(days=now().weekday())
    vendor_ids = UserActivity.objects.filter(login_date__gte=start_of_week, user__role='user').values_list('user', flat=True).distinct()
    vendors = User.objects.filter(id__in=vendor_ids)
    return render(request, 'analytics/list.html', {'title': 'Weekly Active Vendors', 'vendors': vendors})

def mau_view(request):
    if not check_admin_permission(request):
        return redirect('home')
    start_of_month = now().replace(day=1)
    vendor_ids = UserActivity.objects.filter(login_date__gte=start_of_month, user__role='user').values_list('user', flat=True).distinct()
    vendors = User.objects.filter(id__in=vendor_ids)
    return render(request, 'analytics/list.html', {'title': 'Monthly Active Vendors', 'vendors': vendors})

def dormant_vendors_view(request):
    if not check_admin_permission(request):
        return redirect('home')
    logged_in_ids = UserActivity.objects.filter(user__role='user').values_list('user_id', flat=True).distinct()
    vendors = User.objects.filter(role='user').exclude(id__in=logged_in_ids)
    return render(request, 'analytics/list.html', {'title': 'Dormant Vendors (Never Logged In)', 'vendors': vendors})


def avg_session_view(request):
    if not check_admin_permission(request):
        return redirect('home')
    activities = UserActivity.objects.filter(user__role='user', end_time__isnull=False)
    vendor_data = defaultdict(list)

    for act in activities:
        duration = datetime.combine(now(), act.end_time) - datetime.combine(now(), act.start_time)
        vendor_data[act.user].append(duration)

    vendor_sessions = []
    for user, sessions in vendor_data.items():
        total_duration = sum(sessions, timedelta())
        total_sessions = len(sessions)
        avg_duration = total_duration / total_sessions if total_sessions else timedelta()

        total_minutes = round(total_duration.total_seconds() / 60, 2)
        avg_minutes = round(avg_duration.total_seconds() / 60, 2)

        vendor_sessions.append({
            'user': user,
            'total_sessions': total_sessions,
            'total_duration': f"{total_minutes} minutes",
            'avg_duration': f"{avg_minutes} minutes"
        })

    return render(request, 'analytics/avg_session.html', {'vendor_sessions': vendor_sessions})



def most_viewed_products(request):
    if not check_admin_permission(request):
        return redirect('home')
    year = request.GET.get('year')
    month = request.GET.get('month')

    queryset = SearchProduct.objects.all()

    if year:
        queryset = queryset.filter(date__year=year)
    if month:
        queryset = queryset.filter(date__month=month)

    data = (
        queryset
        .values('product__name')
        .annotate(view_count=Count('id'))
        .order_by('-view_count')[:10]
    )

    current_year = datetime.now().year
    year_options = range(current_year - 5, current_year + 1)

    month_options = [
        {'value': i, 'name': datetime(1900, i, 1).strftime('%B')} for i in range(1, 13)
    ]

    return render(request, 'analytics/most_viewed_products.html', {
        'products': data,
        'selected_year': year,
        'selected_month': month,
        'years': year_options,
        'months': month_options
    })



def hero_products(request):
    if not check_admin_permission(request):
        return redirect('home')

    time_filter = request.GET.get('time', 'month')
    metric_filter = request.GET.get('metric', 'all')

    # Calculate time range
    now_time = now()
    if time_filter == 'today':
        start_date = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_filter == 'year':
        start_date = now_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # default to month
        start_date = now_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Initialize empty set
    product_ids = set()

    if metric_filter in ['searched', 'all']:
        searched = SearchProduct.objects.filter(date__range=(start_date, now_time))\
            .values('product__id').annotate(count=Count('id')).order_by('-count')[:5]
        product_ids.update([entry['product__id'] for entry in searched])

    if metric_filter in ['downloaded', 'all']:
        downloaded = AttachmentDownloadLog.objects.filter(downloaded_at__range=(start_date, now_time))\
            .values('product__id').annotate(count=Count('id')).order_by('-count')[:5]
        product_ids.update([entry['product__id'] for entry in downloaded])

    if metric_filter in ['quoted', 'all']:
        quoted = RequestLog.objects.filter(date__range=(start_date, now_time))\
            .values('product__id').annotate(count=Count('id')).order_by('-count')[:5]
        product_ids.update([entry['product__id'] for entry in quoted])

    products = Product.objects.filter(id__in=product_ids)

    return render(request, 'analytics/hero_products.html', {
        'products': products,
        'selected_time': time_filter,
        'selected_metric': metric_filter
    })
def top_categories_engagement(request):
    if not check_admin_permission(request):
        return redirect('home')

    year = request.GET.get('year')
    month = request.GET.get('month')

    queryset = SearchProduct.objects.all()
    if year:
        queryset = queryset.filter(date__year=year)
    if month:
        queryset = queryset.filter(date__month=month)

    data = (
        queryset
        .values('product__product_type__product_category__name')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )

    current_year = datetime.now().year
    year_options = range(current_year - 5, current_year + 1)
    month_options = [
        {'value': i, 'name': datetime(1900, i, 1).strftime('%B')} for i in range(1, 13)
    ]

    return render(request, 'analytics/top_categories.html', {
        'categories': data,
        'selected_year': year,
        'selected_month': month,
        'years': year_options,
        'months': month_options
    })

def most_downloaded_brochures(request):
    if not check_admin_permission(request):
        return redirect('home')

    year = request.GET.get('year')
    month = request.GET.get('month')

    queryset = AttachmentDownloadLog.objects.all()

    if year:
        queryset = queryset.filter(downloaded_at__year=year)
    if month:
        queryset = queryset.filter(downloaded_at__month=month)

    data = (
        queryset
        .values('product__name')
        .annotate(downloads=Count('id'))
        .order_by('-downloads')[:10]
    )

    current_year = datetime.now().year
    year_options = range(current_year - 5, current_year + 1)
    month_options = [
        {'value': i, 'name': datetime(1900, i, 1).strftime('%B')} for i in range(1, 13)
    ]

    return render(request, 'analytics/most_downloaded.html', {
        'downloads': data,
        'selected_year': year,
        'selected_month': month,
        'years': year_options,
        'months': month_options
    })


def most_requested_products(request):
    if not check_admin_permission(request):
        return redirect('home')

    year = request.GET.get('year')
    month = request.GET.get('month')

    queryset = RequestLog.objects.all()

    if year:
        queryset = queryset.filter(date__year=year)
    if month:
        queryset = queryset.filter(date__month=month)

    data = (
        queryset
        .values('product__name')
        .annotate(requests=Count('id'))
        .order_by('-requests')[:10]
    )

    current_year = datetime.now().year
    year_options = range(current_year - 5, current_year + 1)
    month_options = [
        {'value': i, 'name': datetime(1900, i, 1).strftime('%B')} for i in range(1, 13)
    ]

    return render(request, 'analytics/most_requested.html', {
        'products': data,
        'selected_year': year,
        'selected_month': month,
        'years': year_options,
        'months': month_options
    })

def support_metrics_view(request):
    if not check_admin_permission(request):
        return redirect('home')
    period = request.GET.get('period', 'month')  
    today = now()

    if period == 'today':
        logs = RequestLog.objects.filter(date__date=today.date())
    elif period == 'year':
        logs = RequestLog.objects.filter(date__year=today.year)
    else: 
        logs = RequestLog.objects.filter(date__year=today.year, date__month=today.month)

    demo_count = logs.filter(request_type__name='Demo').count()
    training_count = logs.filter(request_type__name='Training').count()
    support_count = logs.filter(request_type__name='Support').count()

    common_issues = (
        logs.filter(request_type__name='Support')
        .values('name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    return render(request, 'analytics/suport_metrix.html', {
        'demo_count': demo_count,
        'training_count': training_count,
        'support_count': support_count,
        'common_issues': common_issues,
        'selected_period': period,
    })



from django.shortcuts import render,redirect

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def admin_only(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'admin':
            return HttpResponseForbidden("Access denied. Admins only.")
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_only
def list_and_create(request, Model, Form, template_name, success_url):
    items = Model.objects.all()
    form = Form(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(success_url)

    return render(request, template_name, {'form': form, 'items': items})


@admin_only
def manage_categories(request):
    return list_and_create(request, Category, CategoryForm, 'analytics/categories.html', 'manage_categories')


@admin_only
def manage_product_categories(request):
    selected_category = request.GET.get('category')
    categories = Category.objects.all()

    queryset = ProductCategory.objects.all()
    if selected_category:
        queryset = queryset.filter(category_id=selected_category)

    # Handle deletion if requested
    if request.method == "POST" and "delete_id" in request.POST:
        delete_id = request.POST.get("delete_id")
        obj = get_object_or_404(ProductCategory, id=delete_id)
        obj.delete()
        return redirect('manage_product_categories')

    form = ProductCategoryForm(request.POST or None)
    if request.method == 'POST' and 'delete_id' not in request.POST and form.is_valid():
        form.save()
        return redirect('manage_product_categories')

    return render(request, 'analytics/product_categories.html', {
        'form': form,
        'items': queryset,
        'categories': categories,
        'selected_category': selected_category
    })


@admin_only
def manage_product_types(request):
    selected_pc = request.GET.get('product_category')
    pcs = ProductCategory.objects.all()

    queryset = ProductType.objects.all()
    if selected_pc:
        queryset = queryset.filter(product_category_id=selected_pc)

    form = ProductTypeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('manage_product_types')

    return render(request, 'analytics/product_types.html', {
        'form': form,
        'items': queryset,
        'product_categories': pcs,
        'selected_pc': selected_pc
    })




@admin_only
def manage_products(request):
    selected_type = request.GET.get('product_type')
    search_query = request.GET.get('search', '')

    queryset = Product.objects.all()

    if selected_type:
        queryset = queryset.filter(product_type_id=selected_type)
    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('manage_products')

    product_types = ProductType.objects.all()

    return render(request, 'analytics/products.html', {
        'form': form,
        'items': queryset,
        'product_types': product_types,
        'selected_type': selected_type
    })

@admin_only
def manage_subproducts(request):
    selected_product = request.GET.get('product')
    products = Product.objects.all()

    queryset = Subproduct.objects.all()
    if selected_product:
        queryset = queryset.filter(product_id=selected_product)

    form = SubproductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('manage_subproducts')

    return render(request, 'analytics/subproducts.html', {
        'form': form,
        'items': queryset,
        'products': products,
        'selected_product': selected_product
    })


from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

@admin_only
@require_POST
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('manage_categories')

@admin_only
@require_POST
def delete_product_category(request, pk):
    pc = get_object_or_404(ProductCategory, pk=pk)
    pc.delete()
    return redirect('manage_product_categories')

@admin_only
@require_POST
def delete_product_type(request, pk):
    pt = get_object_or_404(ProductType, pk=pk)
    pt.delete()
    return redirect('manage_product_types')

@admin_only
@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('manage_products')

@admin_only
@require_POST
def delete_subproduct(request, pk):
    subproduct = get_object_or_404(Subproduct, pk=pk)
    subproduct.delete()
    return redirect('manage_subproducts')
