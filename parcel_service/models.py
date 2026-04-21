from django.db import models
from django.conf import settings

class Parcel(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Pickup'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_parcels')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivered_parcels')
    
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    dimensions = models.CharField(max_length=100, help_text="e.g., 20x20x15 cm", blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    otp = models.CharField(max_length=4, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Parcel {self.id} : {self.pickup_location} -> {self.dropoff_location} ({self.status})"
