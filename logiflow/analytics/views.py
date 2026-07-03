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
    from datetime import timedelta
    now = timezone.now()
    two_weeks_ago = now - timedelta(days=14)

    # Deliveries per day (last 14 days)
    deliveries = Delivery.objects.filter(created__gte=two_weeks_ago)
    
    perDayMap = {}
    peakHourMap = {f"{h:02d}:00": 0 for h in range(24)}
    
    for i in range(14, -1, -1):
        d = (now - timedelta(days=i)).strftime("%b %-d")
        perDayMap[d] = {"deliveries": 0, "avgMinutes": 0, "totalMin": 0}
        
    for d in deliveries:
        date_str = d.created.strftime("%b %-d")
        if date_str in perDayMap:
            perDayMap[date_str]["deliveries"] += 1
            if d.eta_minutes:
                perDayMap[date_str]["totalMin"] += d.eta_minutes
        
        hour_str = d.created.strftime("%H:00")
        if hour_str in peakHourMap:
            peakHourMap[hour_str] += 1
            
    perDay = []
    for k, v in perDayMap.items():
        avg = round(v["totalMin"] / v["deliveries"]) if v["deliveries"] > 0 else 0
        perDay.append({"date": k, "deliveries": v["deliveries"], "avgMinutes": avg})
        
    peakHours = [{"hour": k, "demand": v} for k, v in peakHourMap.items()]
    
    drivers = Driver.objects.all().order_by('-on_time_rate')[:8]
    driverEfficiency = [{"name": d.user.username, "score": int(d.on_time_rate * 100), "deliveries": d.deliveries_completed} for d in drivers]
    
    return Response({
        "perDay": perDay,
        "peakHours": peakHours,
        "driverEfficiency": driverEfficiency
    })
