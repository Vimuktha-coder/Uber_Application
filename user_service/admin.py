from django.contrib import admin
from django.apps import apps
from .models import User, DriverApplication

@admin.action(description="Approve selected applications and upgrade user to Driver")
def approve_driver_applications(modeladmin, request, queryset):
    for app in queryset:
        if app.status == 'pending':
            app.status = 'approved'
            app.save()
            
            # Upgrade the user's role to Driver organically
            user = app.user
            user.role = 'driver'
            user.save()

class DriverApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_make', 'vehicle_model', 'license_plate', 'status', 'submitted_at')
    list_filter = ('status',)
    actions = [approve_driver_applications]

admin.site.register(DriverApplication, DriverApplicationAdmin)

# Register the remaining basic models generically
app = apps.get_app_config('user_service')
for model_name, model in app.models.items():
    if model_name != 'driverapplication':
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
