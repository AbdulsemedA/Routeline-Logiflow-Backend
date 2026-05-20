from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Driver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_driver_profile(sender, instance, **kwargs):
    if instance.role == "driver":
        Driver.objects.get_or_create(
            user=instance,
            defaults={
                "phone": "",
                "vehicle_type": "van",
                "vehicle_plate": "",
                "vehicle_capacity_kg": 0.0,
            },
        )
