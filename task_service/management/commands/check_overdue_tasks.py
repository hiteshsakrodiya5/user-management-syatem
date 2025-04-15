from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from task_service.models import Task
from user_service.models import User


class Command(BaseCommand):
    help = "Check for overdue tasks and deactivate users if needed"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        users = User.objects.filter(role="user", is_active=True)
        for user in users:
            missed_tasks = Task.objects.filter(
                assigned_to=user, status="assigned", deadline__lt=now
            )

            missed_count = missed_tasks.count()

            if missed_count > 5:
                send_mail(
                    subject="User missed task deadline",
                    message=f"User {user.username} missed {missed_count} tasks.",
                    from_email="abc@gmail.com",  # Replace it with verified email
                    recipient_list=["xyz@gmail.com"],  # Replace it with manager email
                )

            if missed_count >= 5:
                user.is_active = False
                user.save()
                self.stdout.write(
                    self.style.WARNING(
                        f"Deactivated {user.username} (missed {missed_count} tasks)"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Overdue task check completed."))
