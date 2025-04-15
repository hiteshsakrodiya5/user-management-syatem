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
    permission_classes = [IsManagerOrAdmin]

    def post(self, request):
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
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
    permission_classes = [IsUserOrAdmin]

    def put(self, request, pk):
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
