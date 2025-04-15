from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (MANAGER, "Manager"),
        (USER, "User"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    missed_tasks = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users"
