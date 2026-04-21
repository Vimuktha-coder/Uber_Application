import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uber_project.settings')
django.setup()
from ride_service.models import VehicleListing
VehicleListing.objects.filter(license_plate__in=['KA-01-AB-1234', 'KA-51-CD-5678', 'KA-05-EF-9012', 'KA-03-GH-3456', 'KA-04-IJ-7890', 'KA-02-KL-1111']).delete()
print('Dummy vehicles removed')
