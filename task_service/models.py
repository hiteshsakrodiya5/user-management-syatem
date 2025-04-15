from django.db import models

from user_service.models import User


# Create your models here.
class Task(models.Model):

    ROLE_CHOICES = [("assigned", "Assigned"), ("completed", "Completed")]

    name = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=ROLE_CHOICES, default="assigned")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "task"
