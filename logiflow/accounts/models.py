from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class ROLES(models.TextChoices):
        ADMIN = "admin", _("Admin")
        DRIVER = "driver", _("Driver")
        CUSTOMER = "customer", _("Customer")
        UNASSIGNED = "unassigned", _("Unassigned")

    role = models.CharField(
        max_length=20, choices=ROLES.choices, default=ROLES.UNASSIGNED
    )
