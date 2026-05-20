from django.contrib.gis.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel

class Driver(TimeStampedModel):
    class STATUSES(models.TextChoices):
        ACTIVE = "active", "Active"
        IDLE = "idle", "Idle"
        OFFLINE = "offline", "Offline"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver_profile")
    phone = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES.choices, default=STATUSES.OFFLINE)
    current_location = models.PointField(null=True, blank=True)
    
    vehicle_type = models.CharField(max_length=20, default="van")
    vehicle_plate = models.CharField(max_length=20, blank=True)
    vehicle_capacity_kg = models.FloatField(default=0.0)
    
    rating = models.FloatField(default=5.0)
    deliveries_completed = models.IntegerField(default=0)
    on_time_rate = models.FloatField(default=1.0)
    active_delivery_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Driver {self.user.username}"
