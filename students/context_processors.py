from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        qs = Notification.objects.filter(user=request.user)
        unread_count        = qs.filter(is_read=False).count()
        recent_notifications = qs.order_by('-created_at')[:6]
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications':       recent_notifications,
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications':       [],
    }
