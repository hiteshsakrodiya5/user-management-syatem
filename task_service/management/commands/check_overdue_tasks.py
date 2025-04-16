from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from task_service.models import Task
from user_service.models import User


class Command(BaseCommand):
    """
    Django management command to check for overdue tasks and deactivate users if needed.

    This command checks all active users with the "user" role and reviews their assigned tasks.
    If a user has missed 5 or more tasks (status "assigned" and deadline passed), they will be:
    - Notified via email about the missed tasks.
    - Deactivated in the system.

    Email notifications will be sent to the manager about any user who missed 5 or more tasks.

    Methods:
        handle(*args, **kwargs): Performs the overdue task check, sends email notifications,
                                   and deactivates users if necessary.
    """

    help = "Check for overdue tasks and deactivate users if needed"

    def handle(self, *args, **kwargs):
        """
        Checks for overdue tasks for each user and deactivates users if they missed 5 or more tasks.

        The method:
        - Retrieves all active users with the "user" role.
        - Checks if any of their assigned tasks are overdue (missed deadline).
        - If a user missed 5 or more tasks, an email is sent to the manager, and the user is deactivated.

        :param args: Command-line arguments passed to the management command.
        :type args: tuple

        :param kwargs: Keyword arguments passed to the management command.
        :type kwargs: dict

        :return: None
        """

        now = timezone.now()
        users = User.objects.filter(role="user", is_active=True)
        for user in users:
            missed_tasks = Task.objects.filter(
                assigned_to=user, status="assigned", deadline__lt=now
            )
            missed_count = missed_tasks.count()

            if missed_count >= 5:
                send_mail(
                    subject="User missed task deadline",
                    message=f"User {user.username} missed {missed_count} tasks.",
                    from_email="hiteshsakrodiya5@gmail.com",  # Replace it with verified email
                    recipient_list=[
                        "hs7898958490@gmail.com"
                    ],  # Replace it with manager email
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
