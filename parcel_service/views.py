from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Parcel
from notification_service.models import Notification
import json
import random

@csrf_exempt
@login_required
def book_parcel(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pickup = data.get('pickup')
            dropoff = data.get('dropoff')
            weight = float(data.get('weight', 1.0))
            
            if not pickup or not dropoff:
                return JsonResponse({'status': 'error', 'message': 'Missing locations'}, status=400)
                
            if weight >= 1000:
                return JsonResponse({'status': 'error', 'message': 'Weight must be less than 1,000 kg'}, status=400)
            
            # Simple pricing logic: 50 base + 10 per kg. We don't route to Stripe for MVP, just pending.
            price = 50 + (weight * 10)
            
            parcel = Parcel.objects.create(
                sender=request.user,
                pickup_location=pickup,
                dropoff_location=dropoff,
                weight_kg=weight,
                price=price,
                status='pending',
                otp=str(random.randint(1000, 9999))
            )
            
            # Notification trigger
            Notification.objects.create(
                user=request.user,
                title="Parcel Booked!",
                message=f"Your {weight}kg parcel from {pickup} is awaiting driver assignment. Cost: ₹{price}"
            )
            
            return JsonResponse({'status': 'success', 'parcel_id': parcel.id, 'price': price})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

@login_required
def parcel_status(request, parcel_id):
    try:
        parcel = Parcel.objects.get(id=parcel_id, sender=request.user)
        data = {
            'status': 'success',
            'parcel_status': parcel.status,
            'driver_name': None,
            'driver_vehicle': None,
            'driver_plate': None,
            'otp': parcel.otp
        }
        
        if parcel.driver:
            from user_service.models import DriverApplication
            data['driver_name'] = parcel.driver.get_full_name() or parcel.driver.username
            app = DriverApplication.objects.filter(user=parcel.driver).first()
            if app:
                data['driver_vehicle'] = f"{app.vehicle_make} {app.vehicle_model}"
                data['driver_plate'] = app.license_plate
                
        return JsonResponse(data)
    except Parcel.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Parcel not found'}, status=404)

@csrf_exempt
@login_required
def auto_assign_parcel(request, parcel_id):
    if request.method == 'POST':
        try:
            parcel = Parcel.objects.get(id=parcel_id, sender=request.user)
            if parcel.status == 'pending':
                from user_service.models import DriverApplication
                # Find any approved driver to test the tracker
                app = DriverApplication.objects.filter(status='approved').first()
                if app:
                    parcel.driver = app.user
                    parcel.status = 'in_transit'
                    parcel.save()
                    return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'noop'})
        except Parcel.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'error': 'POST only'}, status=405)
