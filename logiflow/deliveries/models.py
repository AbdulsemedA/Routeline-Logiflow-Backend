import uuid
from django.contrib.gis.db import models
from model_utils.models import TimeStampedModel

class Delivery(TimeStampedModel):
    class STATUSES(models.TextChoices):
        PENDING = "pending", "Pending"
        ASSIGNED = "assigned", "Assigned"
        PICKED_UP = "picked_up", "Picked Up"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    id = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    customer_id = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=255)
    
    pickup = models.PointField(null=True)
    dropoff = models.PointField(null=True)
    
    package_description = models.CharField(max_length=255)
    package_weight_kg = models.FloatField()
    package_fragile = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUSES.choices, default=STATUSES.PENDING)
    assigned_driver = models.ForeignKey("drivers.Driver", on_delete=models.SET_NULL, null=True, blank=True, related_name="deliveries")
    
    eta_minutes = models.IntegerField(null=True, blank=True)
    distance_km = models.FloatField(default=0.0)
    price_usd = models.FloatField(default=0.0)
    
    route = models.JSONField(default=list)
    events = models.JSONField(default=list)

    def __str__(self):
        return f"Delivery {self.id}"
