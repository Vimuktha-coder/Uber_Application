from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def list_notifications(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = []
    for n in notifs:
        data.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%I:%M %p, %b %d')
        })
    return JsonResponse({'status': 'success', 'notifications': data})
