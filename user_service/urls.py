from django.urls import path

from user_service.views import (
    LoginView,
    LogoutView,
    RegisterView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserUpdateByManager,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user_register"),
    path("login/", LoginView.as_view(), name="user_login"),
    path("fetchUsers/", UserListView.as_view(), name="user_list"),
    path("getUser/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("updateUser/<int:pk>/", UserUpdateByManager.as_view(), name="user_update"),
    path("logout/", LogoutView.as_view(), name="user_logout"),
    path("deleteUser/", UserDeleteView.as_view(), name="user_delete"),
]
