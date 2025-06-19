from django.http import HttpResponse
from django.shortcuts import render
from collections import defaultdict
from datetime import datetime, timedelta, time
from django.utils.timezone import now
from django.db.models import Count, F, ExpressionWrapper, DurationField, Sum
from products.models import SearchProduct, OrderProductOnline, Wishlist
from accounts.models import User, UserActivity
from services.models import RequestLog

def to_time(val):
    """Convert various time formats to time object"""
    if isinstance(val, time):
        return val
    elif isinstance(val, datetime):
        return val.time()
    elif isinstance(val, str):
        try:
            # Try ISO format first (handles datetime strings like "2024-01-01T10:30:00")
            return datetime.fromisoformat(val.replace('Z', '+00:00')).time()
        except (ValueError, AttributeError):
            try:
                # Fallback to time-only format
                return datetime.strptime(val, "%H:%M:%S").time()
            except ValueError:
                try:
                    # Try another common format
                    return datetime.strptime(val, "%H:%M").time()
                except ValueError:
                    return None
    return None

def calculate_session_duration(start_time, end_time, reference_date):
    """Calculate duration between start and end times"""
    try:
        start_time_obj = to_time(start_time)
        end_time_obj = to_time(end_time)
        
        if not start_time_obj or not end_time_obj:
            return timedelta(0)
            
        start_datetime = datetime.combine(reference_date, start_time_obj)
        end_datetime = datetime.combine(reference_date, end_time_obj)
        
        # Handle cases where end time is on the next day
        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)
            
        return end_datetime - start_datetime
    except Exception:
        return timedelta(0)

def home_view(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        today = now()
        period = request.GET.get('period', 'month')

        # Filters for search and order stats
        if period == "today":
            search_filter = {'date__date': today.date()}
            order_filter = {'order_date__date': today.date()}
        elif period == "year":
            search_filter = {'date__year': today.year}
            order_filter = {'order_date__year': today.year}
        else:  # default to month
            search_filter = {'date__month': today.month, 'date__year': today.year}
            order_filter = {'order_date__month': today.month, 'order_date__year': today.year}

        # Top Searched Products
        searches = (
            SearchProduct.objects.filter(**search_filter)
            .values('product__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        # Top Ordered Products
        orders = (
            OrderProductOnline.objects.filter(**order_filter)
            .values('product__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        # Top Users by Session Duration - FIXED VERSION
        try:
            activity = UserActivity.objects.exclude(end_time=None).exclude(start_time=None)
            user_durations = defaultdict(timedelta)
            
            for a in activity:
                if a.end_time and a.start_time and a.user:
                    duration = calculate_session_duration(a.start_time, a.end_time, today.date())
                    if duration > timedelta(0):  # Only add positive durations
                        user_durations[a.user.username] += duration

            # Sort by duration (descending) - FIXED SORTING
            top_users = sorted(
                [{'user__username': user, 'total_duration': str(duration)} for user, duration in user_durations.items()],
                key=lambda x: user_durations[x['user__username']],  # Sort by actual timedelta object
                reverse=True
            )[:5]
            
        except Exception as e:
            # Fallback in case of errors
            top_users = []

        # Most Wishlisted Products
        wishlist_data = (
            Wishlist.objects.filter(is_active=True)
            .values('product__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        # VENDOR ANALYTICS
        all_vendors = User.objects.filter(role='user')
        total_vendors = all_vendors.count()

        last_30_days = today - timedelta(days=30)
        active_vendors_30_days = UserActivity.objects.filter(
            login_date__gte=last_30_days,
            user__role='user'
        ).values('user').distinct().count()

        vendors_logged_in_once = UserActivity.objects.filter(
            user__role='user'
        ).values('user').distinct().count()

        # New Vendors this week/month
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)

        new_vendors_week = all_vendors.filter(date_joined__gte=start_of_week).count()
        new_vendors_month = all_vendors.filter(date_joined__gte=start_of_month).count()

        # Daily/Weekly/Monthly Active Vendors (DAU/WAU/MAU)
        dau = UserActivity.objects.filter(
            login_date=today.date(),
            user__role='user'
        ).values('user').distinct().count()

        wau = UserActivity.objects.filter(
            login_date__gte=start_of_week,
            user__role='user'
        ).values('user').distinct().count()

        mau = UserActivity.objects.filter(
            login_date__gte=start_of_month,
            user__role='user'
        ).values('user').distinct().count()

        # Dormant Vendors (Never Logged In)
        vendors_who_logged_in = UserActivity.objects.filter(
            user__role='user'
        ).values_list('user_id', flat=True).distinct()
        dormant_vendors = all_vendors.exclude(id__in=vendors_who_logged_in).count()

        # Vendor Retention Rate (simple version based on login overlap this and last week)
        last_week_start = start_of_week - timedelta(weeks=1)
        last_week_end = start_of_week - timedelta(days=1)

        retained_this_week = UserActivity.objects.filter(
            user__role='user',
            login_date__range=(start_of_week, today.date())
        ).values_list('user', flat=True).distinct()

        retained_last_week = UserActivity.objects.filter(
            user__role='user',
            login_date__range=(last_week_start, last_week_end)
        ).values_list('user', flat=True).distinct()

        retained_overlap = len(set(retained_this_week).intersection(set(retained_last_week)))
        retention_rate = round((retained_overlap / len(retained_last_week)) * 100, 2) if retained_last_week else 0.0

        # Average Session Duration per Vendor - IMPROVED VERSION
        try:
            # Use database-level duration calculation where possible
            duration_expr = ExpressionWrapper(
                F('end_time') - F('start_time'),
                output_field=DurationField()
            )

            avg_session_data = (
                UserActivity.objects.filter(
                    user__role='user', 
                    end_time__isnull=False,
                    start_time__isnull=False
                )
                .annotate(duration=duration_expr)
                .values('user')
                .annotate(total_duration=Sum('duration'))
            )

            # Calculate average session duration
            if avg_session_data:
                total_seconds = sum([
                    entry['total_duration'].total_seconds() 
                    for entry in avg_session_data 
                    if entry['total_duration']
                ], 0.0)
                avg_session_duration_minutes = round(total_seconds / len(avg_session_data) / 60, 2)
            else:
                avg_session_duration_minutes = 0.0
                
        except Exception as e:
            # Fallback calculation
            avg_session_duration_minutes = 0.0

        # Support/Demo/Training Requests
        support_logs = RequestLog.objects.filter(date__year=today.year, date__month=today.month)

        demo_count = support_logs.filter(request_type__name='Demo').count()
        training_count = support_logs.filter(request_type__name='Training').count()
        support_count = support_logs.filter(request_type__name='Support').count()

        common_issues = (
            support_logs.filter(request_type__name='Support')
            .values('name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        return render(request, 'admin.html', {
            'search_data': list(searches),
            'order_data': list(orders),
            'top_users': list(top_users),
            'wishlist_data': list(wishlist_data),
            'total_vendors': total_vendors,
            'active_vendors_30_days': active_vendors_30_days,
            'vendors_logged_in_once': vendors_logged_in_once,
            'new_vendors_week': new_vendors_week,
            'new_vendors_month': new_vendors_month,
            'dau': dau,
            'wau': wau,
            'mau': mau,
            'dormant_vendors': dormant_vendors,
            'retention_rate': retention_rate,
            'avg_session_duration_minutes': avg_session_duration_minutes,
            'support_count': support_count,
            'demo_count': demo_count,
            'training_count': training_count,
            'common_issues': list(common_issues),
        })

    return render(request, 'base.html')