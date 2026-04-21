"""
URL configuration for uber_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from uber_project import views as core_views
from user_service import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.index, name='index'),
    path('dashboard/', core_views.dashboard, name='dashboard'),
    path('driver/', core_views.driver_dashboard, name='driver_dashboard'),
    path('rentals/', core_views.rentals, name='rentals'),
    path('list-vehicle/', core_views.list_vehicle, name='list_vehicle'),
    path('parcel/', core_views.parcel, name='parcel'),
    path('login/', user_views.login_view, name='login'),
    path('signup/', user_views.register_view, name='signup'),
    path('verify/', user_views.verify_view, name='verify'),
    path('logout/', user_views.logout_view, name='logout'),
    path('apply-to-drive/', user_views.apply_driver_view, name='apply_driver'),
    path('api/', include('ride_service.urls')),
    path('payment/', include('payment_service.urls')),
    path('parcel_api/', include('parcel_service.urls')),
    path('notification_api/', include('notification_service.urls')),
]
