from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Payment
from ride_service.models import Ride
from parcel_service.models import Parcel
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

from django.contrib.auth.decorators import login_required
from notification_service.models import Notification

@csrf_exempt
@login_required
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount', 0))
            ride_id = data.get('ride_id')
            parcel_id = data.get('parcel_id')
            rental_id = data.get('rental_id')
            
            if amount <= 0:
                return JsonResponse({'error': 'Invalid amount'}, status=400)
                
            user = request.user
            
            # Determine booking type dynamically
            booking_type = "Uber Clone Ride Booking"
            base_url = "/payment/success/"
            cancel_base_url = "/payment/cancel/"
            qs = f"?session_id={{CHECKOUT_SESSION_ID}}"
            
            if rental_id:
                booking_type = "Uber Rentals Reservation"
                qs += f"&rental_id={rental_id}"
                cancel_qs = f"?rental_id={rental_id}"
            elif parcel_id:
                booking_type = "Uber Connect Parcel Delivery"
                qs += f"&parcel_id={parcel_id}"
                cancel_qs = f"?parcel_id={parcel_id}"
            else:
                qs += f"&ride_id={ride_id}"
                cancel_qs = f"?ride_id={ride_id}"
            
            # Using INR because the UI prices are in Rupee (₹)
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'unit_amount': int(amount * 100),
                            'product_data': {
                                'name': f"{booking_type} (≈ ${(amount/83.5):.2f})",
                            },
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=request.build_absolute_uri(base_url) + qs,
                cancel_url=request.build_absolute_uri(cancel_base_url) + cancel_qs,
                client_reference_id=str(user.id)
            )
            
            # Create pending Payment record matching the session ID
            payment = Payment.objects.create(
                user=user,
                amount=amount,
                status='pending',
                transaction_id=checkout_session.id
            )
            
            if ride_id and str(ride_id) != 'None':
                try:
                    payment.ride = Ride.objects.get(id=ride_id)
                    payment.save()
                except Ride.DoesNotExist:
                    pass
            elif parcel_id and str(parcel_id) != 'None':
                try:
                    payment.parcel = Parcel.objects.get(id=parcel_id)
                    payment.save()
                except Parcel.DoesNotExist:
                    pass
            elif rental_id and str(rental_id) != 'None':
                try:
                    from ride_service.models import Rental
                    payment.rental = Rental.objects.get(id=rental_id)
                    payment.save()
                except Exception:
                    pass
            
            # Return the generated checkout URL and ID to redirect the user
            return JsonResponse({'url': checkout_session.url, 'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def payment_success_callback(request):
    session_id = request.GET.get('session_id')
    ride_id = request.GET.get('ride_id')
    parcel_id = request.GET.get('parcel_id')
    rental_id = request.GET.get('rental_id')
    
    if session_id:
        try:
            payment = Payment.objects.get(transaction_id=session_id)
            payment.status = 'completed'
            payment.save()
            print(f"[STRIPE SUCCESS] Payment {payment.id} completed via Checkout.")
            
            # Fire Notification for successful booking
            msg = "Your payment of ₹{} was successful. Driver is en route!".format(payment.amount)
            Notification.objects.create(
                user=payment.user,
                title="Payment Confirmed!",
                message=msg
            )
            
        except Payment.DoesNotExist:
            print("[STRIPE WARNING] Payment not found for session:", session_id)
            
    if rental_id and rental_id != 'None':
        try:
            from ride_service.models import Rental
            rental = Rental.objects.get(id=rental_id)
            if rental.status in ['pending', 'pending_payment']:
                rental.status = 'accepted'
                rental.save()
        except: pass
        return redirect(f'/rentals/?payment_success=true&rental_id={rental_id}')
    if parcel_id and parcel_id != 'None':
        try:
            from parcel_service.models import Parcel
            parcel = Parcel.objects.get(id=parcel_id)
            if parcel.status in ['pending', 'pending_payment']:
                parcel.status = 'requested'
                parcel.save()
        except: pass
        return redirect(f'/parcel/?payment_success=true&parcel_id={parcel_id}')
        
    try:
        from ride_service.models import Ride
        ride = Ride.objects.get(id=ride_id)
        if ride.status == 'pending_payment':
            ride.status = 'requested'
            ride.save()
    except: pass
    
    return redirect(f'/dashboard/?payment_success=true&ride_id={ride_id}')

def payment_cancel_callback(request):
    parcel_id = request.GET.get('parcel_id')
    rental_id = request.GET.get('rental_id')
    
    if rental_id and rental_id != 'None':
        return redirect('/rentals/?payment_cancel=true')
    elif parcel_id and parcel_id != 'None':
        return redirect('/parcel/?payment_cancel=true')
        
    return redirect('/dashboard/?payment_cancel=true')
