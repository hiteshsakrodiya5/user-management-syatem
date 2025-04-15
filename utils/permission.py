from rest_framework import permissions


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Allows access only to users with role 'Manager or Admin'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == "manager" or request.user.role == "admin"
        )


class IsUserOrAdmin(permissions.BasePermission):
    """
    Allows access only to users with role 'User or Admin'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == "user" or request.user.role == "admin"
        )
