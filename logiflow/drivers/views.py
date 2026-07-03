from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Driver
from .serializers import DriverSerializer

class DriverListView(generics.ListAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]

class DriverDetailView(generics.RetrieveAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def nearby_drivers(request):
    lat = request.query_params.get("lat")
    lng = request.query_params.get("lng")
    if not lat or not lng:
        return Response({"error": "Provide lat and lng"}, status=400)
    
    point = Point(float(lng), float(lat), srid=4326)
    drivers = Driver.objects.annotate(distance=Distance("current_location", point)).order_by("distance")[:10]
    return Response(DriverSerializer(drivers, many=True).data)

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def update_location(request):
    lat = request.data.get("lat")
    lng = request.data.get("lng")
    if not lat or not lng:
        return Response({"error": "Provide lat and lng"}, status=400)
    
    driver = getattr(request.user, "driver_profile", None)
    if not driver:
        return Response({"error": "User is not a driver"}, status=400)
    
    driver.current_location = Point(float(lng), float(lat), srid=4326)
    driver.save()
    
    from logiflow.realtime.emitters import emit_driver_move
    emit_driver_move(str(driver.id), {"lat": float(lat), "lng": float(lng)})
    
    return Response(DriverSerializer(driver).data)

@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_status(request):
    status = request.data.get("status")
    driver = getattr(request.user, "driver_profile", None)
    if not driver:
        return Response({"error": "User is not a driver"}, status=400)
    
    if status in dict(Driver.STATUSES.choices):
        driver.status = status
        driver.save()
    
    return Response(DriverSerializer(driver).data)
