from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from task_service.models import Task
from task_service.serializer import (
    TaskCreateSerializer,
    TaskSerializer,
    UpdateTaskStatusSerializer,
)
from utils.permission import IsManagerOrAdmin, IsUserOrAdmin


class TaskAssignmentView(APIView):
    """
    API view to assign a task to a user.

    Only users with Manager or Admin roles (based on the IsManagerOrAdmin permission class)
    are authorized to assign tasks.

    Permissions:
        - Requires custom IsManagerOrAdmin permission.

    Methods:
        post(request): Assigns a new task to a user.
    """

    permission_classes = [IsManagerOrAdmin]

    def post(self, request):
        """
        Assigns a new task to a user.

        :param request: HTTP request object containing the task details (name, description, assigned user, deadline).
        :type request: rest_framework.request.Request

        :return: Response containing success message or error details.
        :rtype: rest_framework.response.Response

        :raises Exception: For any unexpected server-side errors while assigning the task.
        """

        try:
            task_serializer = TaskCreateSerializer(data=request.data)
            if task_serializer.is_valid():
                task_data = task_serializer.validated_data
                task = Task.objects.create(
                    name=task_data.get("name"),
                    description=task_data.get("description"),
                    assigned_to=task_data.get("assigned_to"),
                    deadline=task_data.get("deadline"),
                )
                return Response(
                    {"detail": "Task assigned successfully"},
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {"detail": task_serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {
                    "detail": "Something went wrong while assigning the task.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TaskUserAssignedCreateView(APIView):
    """
    API view to retrieve tasks assigned to the authenticated user.

    This endpoint returns tasks based on the authenticated user's role:
    - Regular users will only see tasks assigned to them.
    - Managers and Admins will see all tasks.

    Permissions:
        - Requires the user to be authenticated.

    Methods:
        get(request): Retrieves tasks assigned to the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Retrieves tasks assigned to the authenticated user or all tasks if the user is a manager/admin.

        :param request: HTTP request object made by an authenticated user.
        :type request: rest_framework.request.Request

        :return: Response containing the list of tasks or error details.
        :rtype: rest_framework.response.Response

        :raises Exception: For any unexpected server-side errors while fetching the tasks.
        """

        try:
            user = request.user
            if user.role == "user":
                tasks = Task.objects.filter(assigned_to=user)
            else:
                tasks = Task.objects.all()
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "detail": "Something went wrong while fetching tasks.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateTaskStatus(APIView):
    """
    API view to update the status of a specific task by its primary key (task ID).

    This endpoint allows users with the appropriate permissions (User or Admin) to update
    the status of a task.

    Permissions:
        - Requires custom IsUserOrAdmin permission.

    Methods:
        put(request, pk): Updates the status of a task specified by its primary key (ID).
    """

    permission_classes = [IsUserOrAdmin]

    def put(self, request, pk):
        """
        Updates the status of a task specified by its primary key (ID).

        :param request: HTTP request object containing the task status data to be updated.
        :type request: rest_framework.request.Request

        :param pk: Primary key of the task whose status is being updated.
        :type pk: int

        :return: Response containing updated task data or error details.
        :rtype: rest_framework.response.Response

        :raises Task.DoesNotExist: If the task with the provided ID is not found.
        :raises Exception: For any unexpected server-side errors while updating the task.
        """

        try:
            task = Task.objects.get(pk=pk)
            serializer = UpdateTaskStatusSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Task.DoesNotExist:
            return Response(
                {"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"detail": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
