from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from .models import Delivery
from .serializers import DeliverySerializer
from logiflow.drivers.models import Driver

class DeliveryListView(generics.ListCreateAPIView):
    queryset = Delivery.objects.all().order_by('-created')
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        data = self.request.data
        pickup_lat, pickup_lng = data.get("pickup", {}).get("lat"), data.get("pickup", {}).get("lng")
        dropoff_lat, dropoff_lng = data.get("dropoff", {}).get("lat"), data.get("dropoff", {}).get("lng")
        
        pickup_pt = Point(float(pickup_lng), float(pickup_lat), srid=4326) if pickup_lat else None
        dropoff_pt = Point(float(dropoff_lng), float(dropoff_lat), srid=4326) if dropoff_lat else None
        
        delivery = serializer.save(pickup=pickup_pt, dropoff=dropoff_pt)
        
        try:
            from logiflow.dispatch.services import assign_driver
            assign_driver.delay(delivery.id)
        except Exception:
            pass  # Celery broker not available — auto-assign skipped

class DeliveryDetailView(generics.RetrieveAPIView):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_status(request, pk):
    try:
        delivery = Delivery.objects.get(pk=pk)
    except Delivery.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
        
    status = request.data.get("status")
    if status in dict(Delivery.STATUSES.choices):
        delivery.status = status
        events = delivery.events or []
        events.append({"status": status})
        delivery.events = events
        
        driver_id = request.data.get("driverId")
        if status == Delivery.STATUSES.ASSIGNED and driver_id:
            try:
                driver = Driver.objects.get(id=driver_id)
                delivery.assigned_driver = driver
                driver.active_delivery_id = str(delivery.id)
                driver.status = Driver.STATUSES.ACTIVE
                driver.save()
                from logiflow.realtime.emitters import emit_socket_event
                emit_socket_event("dispatch:assigned", {"deliveryId": str(delivery.id), "driverId": str(driver.id)})
            except Driver.DoesNotExist:
                pass
        
        elif status in (Delivery.STATUSES.DELIVERED, Delivery.STATUSES.CANCELLED):
            driver = delivery.assigned_driver
            if driver:
                driver.active_delivery_id = None
                driver.status = Driver.STATUSES.IDLE
                if status == Delivery.STATUSES.DELIVERED:
                    driver.deliveries_completed += 1
                driver.save()
        
        delivery.save()
        
        from logiflow.realtime.emitters import emit_delivery_status
        emit_delivery_status(delivery.id, status)
        
    return Response(DeliverySerializer(delivery).data)
