import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uber_project.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
from ride_service.models import VehicleListing
from user_service.models import DriverApplication

host = User.objects.filter(role='driver').first() or User.objects.first()
if host:
    host.role = 'driver'
    host.save()

data = [
    {'make': 'Hyundai', 'model': 'Creta', 'plate': 'KA-01-AB-1234', 'city': 'Indiranagar, Bangalore', 'price': 2500},
    {'make': 'Maruti', 'model': 'Swift', 'plate': 'KA-51-CD-5678', 'city': 'Koramangala, Bangalore', 'price': 1200},
    {'make': 'Tata', 'model': 'Nexon', 'plate': 'KA-05-EF-9012', 'city': 'Whitefield, Bangalore', 'price': 2000},
    {'make': 'Mahindra', 'model': 'Thar', 'plate': 'KA-03-GH-3456', 'city': 'Jayanagar, Bangalore', 'price': 3500},
    {'make': 'Honda', 'model': 'City', 'plate': 'KA-04-IJ-7890', 'city': 'HSR Layout, Bangalore', 'price': 1800},
    {'make': 'Kia', 'model': 'Seltos', 'plate': 'KA-02-KL-1111', 'city': 'Yelahanka, Bangalore', 'price': 2800}
]

for v in data:
    VehicleListing.objects.create(host=host, vehicle_make=v['make'], vehicle_model=v['model'], license_plate=v['plate'], location_city=v['city'], daily_price=v['price'], is_available=True)

DriverApplication.objects.get_or_create(user=host, defaults={'vehicle_make': 'Maruti', 'vehicle_model': 'Dzire', 'license_plate': 'KA-01-ZZ-9999', 'status': 'approved'})

print('Success')
