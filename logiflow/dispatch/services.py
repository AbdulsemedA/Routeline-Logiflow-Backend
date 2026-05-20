from celery import shared_task
from django.contrib.gis.db.models.functions import Distance
from logiflow.drivers.models import Driver
from logiflow.deliveries.models import Delivery
from logiflow.realtime.emitters import emit_delivery_status, emit_socket_event

@shared_task
def assign_driver(delivery_id):
    try:
        delivery = Delivery.objects.get(id=delivery_id)
    except Delivery.DoesNotExist:
        return

    if not delivery.pickup: return
    
    nearest_drivers = Driver.objects.filter(status=Driver.STATUSES.ACTIVE).annotate(
        distance=Distance("current_location", delivery.pickup)
    ).order_by("distance")
    
    if nearest_drivers.exists():
        driver = nearest_drivers.first()
        delivery.assigned_driver = driver
        delivery.status = Delivery.STATUSES.ASSIGNED
        events = delivery.events or []
        events.append({"status": "assigned"})
        delivery.events = events
        delivery.save()
        
        driver.active_delivery_id = str(delivery.id)
        driver.save()
        
        emit_delivery_status(delivery.id, "assigned")
        emit_socket_event("dispatch:assigned", {"deliveryId": str(delivery.id), "driverId": str(driver.id)})
