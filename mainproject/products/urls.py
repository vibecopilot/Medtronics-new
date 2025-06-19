# urls.py (in your app)
from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.category_view, name='category_list'),
    path('productskey/<int:pk>/', views.product_category_view, name='product_list'),
    path('product/detail/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),  # Ensure this path is correct
    path('store-searched-product/', views.store_searched_product, name='store_searched_product'),
    path('products/<int:product_id>/toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('products/order/<int:product_id>/', views.order_product_online_view, name='order_product_online'),
    path('ajax/product-categories/', views.ajax_product_categories, name='ajax_product_categories'),
    path('ajax/product-types/', views.ajax_product_types, name='ajax_product_types'),
    path('ajax/products/', views.ajax_products, name='ajax_products'),
    path('subproduct/detail/<int:pk>/', views.subproduct_detail_view, name='subproduct_detail'),

]
