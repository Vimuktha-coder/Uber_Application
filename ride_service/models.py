from django.db import models
from django.conf import settings

class Ride(models.Model):
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rides_as_passenger')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rides_as_driver')
    
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    fare = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    vehicle_type = models.CharField(max_length=50, default='Uber Go')
    otp = models.CharField(max_length=4, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride {self.id} : {self.pickup_location} -> {self.dropoff_location}"

class VehicleListing(models.Model):
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicle_listings')
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    license_plate = models.CharField(max_length=20)
    location_city = models.CharField(max_length=100)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vehicle_make} {self.vehicle_model} - {self.host.username}"

class Rental(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rentals_as_passenger')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rentals_as_driver')
    selected_vehicle = models.ForeignKey(VehicleListing, on_delete=models.SET_NULL, null=True, blank=True)
    
    pickup_location = models.CharField(max_length=255)
    duration_hours = models.IntegerField(default=1)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    otp = models.CharField(max_length=4, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rental {self.id} : {self.duration_hours} Hrs from {self.pickup_location}"
