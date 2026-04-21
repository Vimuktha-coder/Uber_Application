from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def dashboard(request):
    context = {
        'pickup': request.GET.get('pickup', ''),
        'dropoff': request.GET.get('dropoff', ''),
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='/login/')
def rentals(request):
    return render(request, 'rentals.html')

@login_required(login_url='/login/')
def parcel(request):
    return render(request, 'parcel.html')

from django.shortcuts import redirect

@login_required(login_url='/login/')
def driver_dashboard(request):
    if getattr(request.user, 'role', '') != 'driver':
        return redirect('/dashboard/')
    return render(request, 'driver_dashboard.html')

@login_required(login_url='/login/')
def list_vehicle(request):
    from ride_service.models import VehicleListing
    vehicle = VehicleListing.objects.filter(host=request.user).first()
    return render(request, 'list_vehicle.html', {'vehicle': vehicle})
