from django.utils import timezone
from rest_framework import serializers

from task_service.models import Task
from user_service.models import User


class TaskCreateSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="user")
    )

    class Meta:
        model = Task
        fields = ["name", "description", "assigned_to", "deadline"]

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def validate(self, data):
        if data["assigned_to"].is_active is False:
            raise serializers.ValidationError(
                "Cannot assign task to a deactivated user."
            )
        return data


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "name", "description", "assigned_to", "deadline", "status"]


class UpdateTaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["status"]
