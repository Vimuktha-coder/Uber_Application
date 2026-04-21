from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_parcel, name='book_parcel'),
    path('parcel-status/<int:parcel_id>/', views.parcel_status, name='parcel_status'),
    path('auto-assign/<int:parcel_id>/', views.auto_assign_parcel, name='auto_assign_parcel'),
]
