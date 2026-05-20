from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from logiflow.deliveries.models import Delivery
from logiflow.drivers.models import Driver
from django.utils import timezone

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def summary(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    completed_today = Delivery.objects.filter(status=Delivery.STATUSES.DELIVERED, modified__gte=today_start).count()
    active_deliveries = Delivery.objects.filter(status__in=[
        Delivery.STATUSES.ASSIGNED, Delivery.STATUSES.PICKED_UP, Delivery.STATUSES.IN_TRANSIT
    ]).count()
    active_drivers = Driver.objects.filter(status=Driver.STATUSES.ACTIVE).count()
    total_drivers = Driver.objects.count()
    
    avg_delivery_min = 25.5 
    
    return Response({
        "activeDeliveries": active_deliveries,
        "activeDrivers": active_drivers,
        "completedToday": completed_today,
        "avgDeliveryMin": avg_delivery_min,
        "totalDrivers": total_drivers
    })

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def series(request):
    perDay = [{"date": "May 1", "deliveries": 60, "avgMinutes": 18}]
    peakHours = [{"hour": "12:00", "demand": 80}]
    
    drivers = Driver.objects.all().order_by('-on_time_rate')[:8]
    driverEfficiency = [{"name": d.user.username, "score": int(d.on_time_rate * 100), "deliveries": d.deliveries_completed} for d in drivers]
    
    return Response({
        "perDay": perDay,
        "peakHours": peakHours,
        "driverEfficiency": driverEfficiency
    })
