import math
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.utils import timezone
from .models import Delivery
from .serializers import DeliverySerializer
from logiflow.drivers.models import Driver


def _haversine_km(lat1, lng1, lat2, lng2):
    """Return the great-circle distance in km between two points."""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


class DeliveryListView(generics.ListCreateAPIView):
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Delivery.objects.all().order_by("-created")

        # Drivers see only their assigned deliveries
        driver = getattr(user, "driver_profile", None)
        if driver:
            return qs.filter(assigned_driver=driver)

        # Customers see only their own deliveries
        role = getattr(user, "role", None)
        if role == "customer":
            return qs.filter(customer_id=str(user.id))

        # Admins / others see everything
        return qs

    def perform_create(self, serializer):
        data = self.request.data
        pickup_data = data.get("pickup", {})
        dropoff_data = data.get("dropoff", {})
        pickup_lat, pickup_lng = pickup_data.get("lat"), pickup_data.get("lng")
        dropoff_lat, dropoff_lng = dropoff_data.get("lat"), dropoff_data.get("lng")

        pickup_pt = Point(float(pickup_lng), float(pickup_lat), srid=4326) if pickup_lat else None
        dropoff_pt = Point(float(dropoff_lng), float(dropoff_lat), srid=4326) if dropoff_lat else None

        # Compute distance, ETA, and price
        distance_km = 0.0
        eta_minutes = None
        price_usd = 0.0
        if pickup_lat and dropoff_lat:
            distance_km = round(_haversine_km(float(pickup_lat), float(pickup_lng), float(dropoff_lat), float(dropoff_lng)), 2)
            eta_minutes = max(1, round((distance_km / 32) * 60))  # ~32 km/h average
            price_usd = round(2.50 + distance_km * 1.20, 2)  # base fare + per-km rate

        pickup_label = pickup_data.get("label", "")
        dropoff_label = dropoff_data.get("label", "")

        initial_event = {"status": "pending", "timestamp": timezone.now().isoformat()}

        delivery = serializer.save(
            pickup=pickup_pt,
            dropoff=dropoff_pt,
            pickup_label=pickup_label,
            dropoff_label=dropoff_label,
            distance_km=distance_km,
            eta_minutes=eta_minutes,
            price_usd=price_usd,
            customer_id=str(self.request.user.id),
            events=[initial_event],
        )

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
        events.append({"status": status, "timestamp": timezone.now().isoformat()})
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

