from django.urls import path
from . import views

urlpatterns = [
    path('', views.vendor_list_view, name='vendor_list'),
    path('active/', views.active_vendors_view, name='active_vendors'),
    path('logged-in/', views.logged_in_vendors_view, name='logged_in_vendors'),
    path('new/week/', views.new_vendors_week_view, name='new_vendors_week'),
    path('new/month/', views.new_vendors_month_view, name='new_vendors_month'),
    path('dau/', views.dau_view, name='dau_vendors'),
    path('wau/', views.wau_view, name='wau_vendors'),
    path('mau/', views.mau_view, name='mau_vendors'),
    path('dormant/', views.dormant_vendors_view, name='dormant_vendors'),
    path('avg-session/', views.avg_session_view, name='avg_session_vendors'),
    path('most-viewed/', views.most_viewed_products, name='most_viewed_products'),
    path('hero-products/', views.hero_products, name='hero_products'),
    path('top-categories/', views.top_categories_engagement, name='top_categories_engagement'),
    path('most-downloaded/', views.most_downloaded_brochures, name='most_downloaded_brochures'),
    path('most-requested/', views.most_requested_products, name='most_requested_products'),
    path('analytics/support-metrics/', views.support_metrics_view, name='support_metrics'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('product-categories/', views.manage_product_categories, name='manage_product_categories'),
    path('product-types/', views.manage_product_types, name='manage_product_types'),
    path('products/', views.manage_products, name='manage_products'),
    path('subproducts/', views.manage_subproducts, name='manage_subproducts'),
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),
    path('delete-product-category/<int:pk>/', views.delete_product_category, name='delete_product_category'),
    path('delete-product-type/<int:pk>/', views.delete_product_type, name='delete_product_type'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('delete-subproduct/<int:pk>/', views.delete_subproduct, name='delete_subproduct'),


]
