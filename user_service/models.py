from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('passenger', 'Passenger'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='passenger')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    rating = models.FloatField(default=5.0)

    def __str__(self):
        return f"{self.username} ({self.role})"

class DriverApplication(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_application')
    vehicle_make = models.CharField(max_length=50) 
    vehicle_model = models.CharField(max_length=50) 
    license_plate = models.CharField(max_length=20)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                orig = DriverApplication.objects.get(pk=self.pk)
                if orig.status != 'approved' and self.status == 'approved':
                    self.user.role = 'driver'
                    self.user.save()
            except DriverApplication.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Driver Application from {self.user.username} ({self.status.upper()})"
