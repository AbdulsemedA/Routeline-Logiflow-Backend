from rest_framework import serializers
from .models import Driver

class VehicleSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    type = serializers.CharField(source="vehicle_type")
    plate = serializers.CharField(source="vehicle_plate")
    capacityKg = serializers.FloatField(source="vehicle_capacity_kg")

class DriverSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.username", read_only=True)
    vehicle = VehicleSerializer(source="*", read_only=True)
    currentLocation = serializers.SerializerMethodField()
    deliveriesCompleted = serializers.IntegerField(source="deliveries_completed", read_only=True)
    onTimeRate = serializers.FloatField(source="on_time_rate", read_only=True)
    activeDeliveryId = serializers.CharField(source="active_delivery_id", read_only=True)

    class Meta:
        model = Driver
        fields = (
            "id", "name", "phone", "status", "currentLocation",
            "vehicle", "rating", "deliveriesCompleted", "onTimeRate", "activeDeliveryId"
        )
        
    def get_currentLocation(self, obj):
        if obj.current_location:
            return {"lat": obj.current_location.y, "lng": obj.current_location.x}
        return {"lat": 0.0, "lng": 0.0}
