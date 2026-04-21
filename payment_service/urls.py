from django.urls import path
from . import views

urlpatterns = [
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success_callback, name='payment_success'),
    path('cancel/', views.payment_cancel_callback, name='payment_cancel'),
]
