from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .models import User
import os
from dotenv import load_dotenv
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings
import random
# Load environment variables
load_dotenv()

def register_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        phone = request.POST.get('phone')
        if phone:
            phone = phone.strip()
            if len(phone) == 10 and phone.isdigit():
                phone = '+91' + phone
        
        if u and p and e and phone:
            if User.objects.filter(username=u).exists():
                return render(request, 'signup.html', {'error': 'That username is already taken. Please choose another.'})
                
            user = User.objects.create_user(username=u, email=e, password=p, phone_number=phone)
            
            # GENERATE OTPS
            email_otp = str(random.randint(1000, 9999))
            sms_otp = email_otp # Identical for testing ease
            
            request.session['registration_username'] = u
            request.session['email_otp'] = email_otp
            request.session['sms_otp'] = sms_otp
            
            # REAL TWILIO DISPATCHER LOGIC
            twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
            twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
            twilio_sender = os.getenv('TWILIO_PHONE_NUMBER')
            
            if twilio_sid and twilio_token and twilio_sender:
                try:
                    client = Client(twilio_sid, twilio_token)
                    client.messages.create(
                        body=f'Your Uber Security Code is {sms_otp}',
                        from_=twilio_sender,
                        to=phone
                    )
                    print(f"\n[SUCCESS] REAL Twilio SMS dispatched to {phone}!")
                except Exception as ex:
                    print(f"\n[TWILIO ERROR] Could not dispatch real SMS: {str(ex)}")
            else:
                # Print to server logs silently if missing API keys
                print(f"\n[TWILIO MOCK] SMS sent to {phone}: 'Your Uber Security Code is {sms_otp}'.")
            
            # SEND REAL EMAIL
            try:
                send_mail(
                    'Your Uber Security Code',
                    f'Your Uber email verification code is {email_otp}',
                    settings.EMAIL_HOST_USER,
                    [e],
                    fail_silently=False,
                )
                print(f"\n[EMAIL SUCCESS] Real email dispatched to {e}!")
            except Exception as ex:
                print(f"\n[EMAIL ERROR] Could not dispatch real email: {str(ex)}")
            
            return redirect('verify')
            
    return render(request, 'signup.html')

def verify_view(request):
    if not request.session.get('registration_username'):
        return redirect('signup')
        
    username = request.session.get('registration_username')
    user = User.objects.get(username=username)
    
    if request.method == 'POST':
        email_code = request.POST.get('email_code')
        sms_code = request.POST.get('sms_code')
        
        if email_code == request.session.get('email_otp') and sms_code == request.session.get('sms_otp'):
            user.is_phone_verified = True
            user.is_email_verified = True
            user.save()
            
            login(request, user)
            request.session.pop('registration_username', None)
            if user.role == 'driver':
                return redirect('/driver/')
            return redirect('/dashboard/')
        else:
            return render(request, 'verify.html', {'error': 'Invalid 4-digit codes provided. Please re-check your messages.', 'phone': user.phone_number, 'username': user.username})
            
    return render(request, 'verify.html', {'phone': user.phone_number, 'email': user.email, 'username': user.username})

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            if user.role == 'driver':
                return redirect('/driver/')
            return redirect('/dashboard/')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def apply_driver_view(request):
    from .models import DriverApplication
    
    app = DriverApplication.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        make = request.POST.get('vehicle_make')
        model = request.POST.get('vehicle_model')
        plate = request.POST.get('license_plate')
        
        if make and model and plate:
            if not app:
                app = DriverApplication.objects.create(user=request.user, vehicle_make=make, vehicle_model=model, license_plate=plate, status='pending')
            else:
                app.vehicle_make = make
                app.vehicle_model = model
                app.license_plate = plate
                app.status = 'pending'
                app.save()
            
            return redirect('apply_driver')
            
    return render(request, 'apply_driver.html', {'application': app})
