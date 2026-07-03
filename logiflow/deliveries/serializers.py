from rest_framework import serializers
from .models import Delivery

class PackageSerializer(serializers.Serializer):
    description = serializers.CharField(source="package_description")
    weightKg = serializers.FloatField(source="package_weight_kg")
    fragile = serializers.BooleanField(source="package_fragile")

class DeliverySerializer(serializers.ModelSerializer):
    customerName = serializers.CharField(source="customer_name")
    customerId = serializers.CharField(source="customer_id")
    assignedDriverId = serializers.CharField(source="assigned_driver.id", read_only=True)
    etaMinutes = serializers.IntegerField(source="eta_minutes", read_only=True)
    distanceKm = serializers.FloatField(source="distance_km", read_only=True)
    priceUsd = serializers.FloatField(source="price_usd", read_only=True)
    
    package = PackageSerializer(source="*")
    pickup = serializers.SerializerMethodField()
    dropoff = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = (
            "id", "customerId", "customerName", "pickup", "dropoff",
            "package", "status", "assignedDriverId", "created",
            "etaMinutes", "distanceKm", "priceUsd", "route", "events"
        )
        
    def get_pickup(self, obj):
        if obj.pickup:
            return {"lat": obj.pickup.y, "lng": obj.pickup.x, "label": obj.pickup_label or None}
        return None

    def get_dropoff(self, obj):
        if obj.dropoff:
            return {"lat": obj.dropoff.y, "lng": obj.dropoff.x, "label": obj.dropoff_label or None}
        return None
