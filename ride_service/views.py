from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
from .models import Ride
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@csrf_exempt
@login_required
def book_ride(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pickup = data.get('pickup')
            dropoff = data.get('dropoff')
            fare = data.get('fare', 0.0)
            vehicle_type = data.get('vehicle_type', 'Uber Go')

            ride = Ride.objects.create(
                passenger=request.user,
                pickup_location=pickup,
                dropoff_location=dropoff,
                fare=fare,
                vehicle_type=vehicle_type,
                status='pending_payment',
                otp=str(random.randint(1000, 9999))
            )
            return JsonResponse({'status': 'success', 'ride_id': ride.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed'}, status=405)

@csrf_exempt
@login_required
def available_rides(request):
    if request.method == 'GET':
        if getattr(request.user, 'role', '') != 'driver':
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
        from django.db.models import Q
        from ride_service.models import Ride, Rental
        from parcel_service.models import Parcel

        rides_data = []

        # Determine Driver's specific vehicle category
        driver_cat = 'Uber Go'
        if hasattr(request.user, 'driver_application'):
            make = request.user.driver_application.vehicle_make.lower()
            model = request.user.driver_application.vehicle_model.lower()
            combined = f"{make} {model}"
            
            if any(x in combined for x in ['bajaj', 'piaggio', 'tvs', 'mahindra', 'auto', 'rickshaw']):
                driver_cat = 'Uber Auto'
            elif any(x in combined for x in ['honda', 'yamaha', 'hero', 'royal enfield', 'suzuki', 'moto', 'bike', 'scooter']):
                driver_cat = 'Moto'

        # Fetch Rides
        rides = Ride.objects.filter(
            Q(status='requested', vehicle_type=driver_cat) | Q(driver=request.user, status__in=['accepted', 'in_progress'])
        ).order_by('-created_at')
        
        for r in rides:
            rides_data.append({
                'type': 'ride',
                'title': f'{r.vehicle_type.upper()} • #{r.id}',
                'id': r.id,
                'status': r.status,
                'pickup': r.pickup_location,
                'dropoff': r.dropoff_location,
                'fare': str(r.fare),
                'passenger': r.passenger.username
            })


        # Fetch Parcels
        parcels = Parcel.objects.filter(
            Q(status='requested') | Q(driver=request.user, status__in=['accepted', 'in_transit'])
        ).order_by('-created_at')
        for p in parcels:
            rides_data.append({
                'type': 'parcel',
                'title': f'Uber Connect',
                'id': p.id,
                'status': p.status,
                'pickup': p.pickup_location,
                'dropoff': p.dropoff_location,
                'fare': str(p.price),
                'passenger': p.sender.username
            })
            
        return JsonResponse({'status': 'success', 'rides': rides_data})
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
@login_required
def accept_trip(request):
    if request.method == 'POST':
        if getattr(request.user, 'role', '') != 'driver':
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        try:
            import json
            data = json.loads(request.body)
            trip_type = data.get('type')
            trip_id = data.get('id')
            
            if trip_type == 'ride':
                trip = Ride.objects.get(id=trip_id, status='requested')
            elif trip_type == 'rental':
                from ride_service.models import Rental
                trip = Rental.objects.get(id=trip_id, status='requested')
            elif trip_type == 'parcel':
                from parcel_service.models import Parcel
                trip = Parcel.objects.get(id=trip_id, status='requested')
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid trip type'}, status=400)
                
            trip.status = 'accepted'
            trip.driver = request.user
            trip.save()
            return JsonResponse({'status': 'success', 'message': 'Trip accepted'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Trip no longer available'}, status=404)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
def auto_assign_ride(request, ride_id):
    # Dev endpoint to automatically assign a REAL database driver to a ride
    if request.method == 'POST':
        try:
            ride = Ride.objects.get(id=ride_id, status='requested')
            # Determine required makes based on vehicle_type
            allowed_makes = []
            if ride.vehicle_type == 'Uber Auto':
                allowed_makes = ['bajaj', 'piaggio', 'tvs', 'mahindra']
            elif ride.vehicle_type == 'Moto':
                allowed_makes = ['honda', 'yamaha', 'hero', 'royal enfield', 'suzuki', 'tvs xl']
                
            driver = None
            if allowed_makes:
                # Try to find a matching driver
                driver = User.objects.filter(role='driver', driver_application__vehicle_make__iregex=r'(' + '|'.join(allowed_makes) + ')').exclude(id=ride.passenger.id).first()
                
            if not driver:
                # Fallback to any valid driver if no specific match
                driver = User.objects.filter(role='driver').exclude(id=ride.passenger.id).first()
            if not driver:
                # Desperate fallback
                driver = User.objects.exclude(id=ride.passenger.id).first()
                
            if driver:
                ride.status = 'accepted'
                ride.driver = driver
                ride.save()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'No other users exist in the database'})
        except Ride.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def ride_status(request, ride_id):
    if request.method == 'GET':
        try:
            ride = Ride.objects.get(id=ride_id, passenger=request.user)
            response_data = {
                'status': 'success',
                'ride_status': ride.status,
                'pickup': ride.pickup_location,
                'dropoff': ride.dropoff_location,
                'fare': str(ride.fare),
                'otp': ride.otp
            }
            
            # If the driver accepted, pull their explicit Application Metadata
            if ride.status == 'accepted' and ride.driver:
                try:
                    driver_app = ride.driver.driver_application
                    response_data['driver'] = {
                        'name': ride.driver.username,
                        'vehicle_make': driver_app.vehicle_make,
                        'vehicle_model': driver_app.vehicle_model,
                        'license_plate': driver_app.license_plate
                    }
                except Exception:
                    response_data['driver'] = {
                        'name': ride.driver.username,
                        'vehicle_make': 'Standard',
                        'vehicle_model': 'Vehicle',
                        'license_plate': 'UNKNOWN'
                    }
            return JsonResponse(response_data)
        except Ride.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ride not found'}, status=404)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
@login_required
def book_rental(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pickup = data.get('pickup')
            days = int(data.get('hours', 1)) # Note: UI passes 'hours' variable representing Days
            vehicle_id = data.get('vehicle_id')
            
            if not pickup or not vehicle_id:
                return JsonResponse({'status': 'error', 'message': 'Missing location or vehicle selection'}, status=400)
                
            from .models import Rental, VehicleListing
            try:
                vehicle = VehicleListing.objects.get(id=vehicle_id, is_available=True)
            except VehicleListing.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Vehicle not available'}, status=404)
                
            price = vehicle.daily_price * days
            
            rental = Rental.objects.create(
                passenger=request.user,
                pickup_location=pickup,
                duration_hours=days * 24,
                price=price,
                selected_vehicle=vehicle,
                driver=vehicle.host,
                status='pending',
                otp=str(random.randint(1000, 9999))
            )
            
            return JsonResponse({'status': 'success', 'rental_id': rental.id, 'price': price, 'hours': days})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def rental_status(request, rental_id):
    try:
        from .models import Rental
        rental = Rental.objects.get(id=rental_id, passenger=request.user)
        data = {
            'status': 'success',
            'rental_status': rental.status,
            'driver_name': None,
            'driver_vehicle': None,
            'driver_plate': None,
            'otp': rental.otp
        }
        
        if rental.driver:
            from user_service.models import DriverApplication
            data['driver_name'] = rental.driver.get_full_name() or rental.driver.username
            app = DriverApplication.objects.filter(user=rental.driver).first()
            if app:
                data['driver_vehicle'] = f"{app.vehicle_make} {app.vehicle_model}"
                data['driver_plate'] = app.license_plate
                
        return JsonResponse(data)
    except Rental.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Rental not found'}, status=404)

@csrf_exempt
@login_required
def auto_assign_rental(request, rental_id):
    if request.method == 'POST':
        try:
            from .models import Rental
            rental = Rental.objects.get(id=rental_id, passenger=request.user)
            if rental.status in ['pending', 'accepted']:
                rental.status = 'active'
                rental.save()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'noop'})
        except Rental.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'error': 'POST only'}, status=405)

@login_required
def get_available_vehicles(request):
    if request.method == 'GET':
        from .models import VehicleListing, Rental
        from django.utils import timezone
        import datetime
        
        now = timezone.now()
        active_rentals = Rental.objects.filter(status__in=['accepted', 'active'])
        
        unavailable_vehicle_ids = []
        for r in active_rentals:
            if r.selected_vehicle:
                expiration_time = r.created_at + datetime.timedelta(hours=r.duration_hours)
                if now < expiration_time:
                    unavailable_vehicle_ids.append(r.selected_vehicle.id)
                    
        vehicles = VehicleListing.objects.filter(is_available=True).exclude(id__in=unavailable_vehicle_ids)
        vehicle_list = []
        for v in vehicles:
            vehicle_list.append({
                'id': v.id,
                'host_name': v.host.username,
                'vehicle_make': v.vehicle_make,
                'vehicle_model': v.vehicle_model,
                'license_plate': v.license_plate,
                'location_city': v.location_city,
                'daily_price': float(v.daily_price)
            })
        return JsonResponse({'status': 'success', 'vehicles': vehicle_list})
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
@login_required
def create_vehicle_listing(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            from .models import VehicleListing
            vehicle = VehicleListing.objects.create(
                host=request.user,
                vehicle_make=data.get('make'),
                vehicle_model=data.get('model'),
                license_plate=data.get('plate'),
                location_city=data.get('city', 'Bangalore'),
                daily_price=data.get('price')
            )
            return JsonResponse({'status': 'success', 'vehicle_id': vehicle.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
@login_required
def verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            trip_type = data.get('type')  # 'ride', 'rental', 'parcel'
            trip_id = data.get('id')
            otp_entered = data.get('otp')
            
            if trip_type == 'ride':
                from .models import Ride
                trip = Ride.objects.get(id=trip_id, driver=request.user)
            elif trip_type == 'rental':
                from .models import Rental
                trip = Rental.objects.get(id=trip_id, driver=request.user)
            elif trip_type == 'parcel':
                from parcel_service.models import Parcel
                trip = Parcel.objects.get(id=trip_id, driver=request.user)
            else:
                return JsonResponse({'status': 'error', 'message': 'Unknown trip type'}, status=400)
                
            if trip.otp and str(trip.otp) == str(otp_entered):
                # Successfully verified! Upgrade status
                if trip_type == 'parcel':
                    trip.status = 'in_transit'
                elif trip_type == 'rental':
                    trip.status = 'active'
                else:
                    trip.status = 'in_progress'
                trip.save()
                return JsonResponse({'status': 'success', 'message': 'OTP verified! Trip started.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Incorrect PIN'}, status=400)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
@login_required
def complete_trip(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            trip_type = data.get('type')
            trip_id = data.get('id')
            
            if trip_type == 'ride':
                from .models import Ride
                trip = Ride.objects.get(id=trip_id, driver=request.user)
            elif trip_type == 'rental':
                from .models import Rental
                trip = Rental.objects.get(id=trip_id, driver=request.user)
            elif trip_type == 'parcel':
                from parcel_service.models import Parcel
                trip = Parcel.objects.get(id=trip_id, driver=request.user)
            else:
                return JsonResponse({'status': 'error', 'message': 'Unknown trip type'}, status=400)
                
            trip.status = 'completed'
            trip.save()
            return JsonResponse({'status': 'success', 'message': 'Trip completed!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@csrf_exempt
@login_required
def cancel_trip(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            trip_type = data.get('type')
            trip_id = data.get('id')
            
            if trip_type == 'ride':
                from .models import Ride
                trip = Ride.objects.get(id=trip_id, driver=request.user)
            elif trip_type == 'rental':
                from .models import Rental
                trip = Rental.objects.get(id=trip_id, driver=request.user)
            elif trip_type == 'parcel':
                from parcel_service.models import Parcel
                trip = Parcel.objects.get(id=trip_id, driver=request.user)
            else:
                return JsonResponse({'status': 'error', 'message': 'Unknown trip type'}, status=400)
                
            trip.status = 'cancelled'
            trip.save()
            return JsonResponse({'status': 'success', 'message': 'Trip cancelled!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)
