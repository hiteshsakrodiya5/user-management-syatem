from django.urls import path

from task_service.views import (
    TaskAssignmentView,
    TaskUserAssignedCreateView,
    UpdateTaskStatus,
)

urlpatterns = [
    path("fetchTask/", TaskUserAssignedCreateView.as_view(), name="task_list_create"),
    path("assign/", TaskAssignmentView.as_view(), name="task_assignment"),
    path("updateStatus/<str:pk>/", UpdateTaskStatus.as_view(), name="update_status"),
]
