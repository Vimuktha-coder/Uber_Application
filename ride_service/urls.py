from django.urls import path
from . import views

urlpatterns = [
    path('book-ride/', views.book_ride, name='book_ride'),
    path('driver/available-rides/', views.available_rides, name='available_rides'),
    path('driver/accept-trip/', views.accept_trip, name='accept_trip'),
    path('auto-assign/<int:ride_id>/', views.auto_assign_ride, name='auto_assign'),
    path('ride-status/<int:ride_id>/', views.ride_status, name='ride_status'),
    path('book-rental/', views.book_rental, name='book_rental'),
    path('rental-status/<int:rental_id>/', views.rental_status, name='rental_status'),
    path('auto-assign-rental/<int:rental_id>/', views.auto_assign_rental, name='auto_assign_rental'),
    path('get-vehicles/', views.get_available_vehicles, name='get_vehicles'),
    path('list-vehicle/', views.create_vehicle_listing, name='create_vehicle_listing'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('driver/complete-trip/', views.complete_trip, name='complete_trip'),
    path('driver/cancel-trip/', views.cancel_trip, name='cancel_trip'),
]
