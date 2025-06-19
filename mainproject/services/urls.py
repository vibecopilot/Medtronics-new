from django.urls import path
from . import views

urlpatterns = [
    
    # path('demo/', views.demo_form_view, name='demo_form'),
    path('training/', views.training_request_view, name='training_form'),  
    path('product/', views.product_request_view, name='product_form'),
    path('demo-request/', views.demo_request_view, name='demo_form'),
    path('training-request/', views.training_request_view, name='training_request'),
    path('product-request/', views.product_request_view, name='product_request'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
]


