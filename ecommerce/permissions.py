from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Non-admin users can only read.
    """

    def has_permission(self, request, view):
        # Allow read-only access for non-authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        # this is the custom permission class that allows only admins to edit objects, while non-admin users can only read them.
        return request.user and request.user.is_authenticated

    # this will check if the user has permission to perform actions on a specific object
    def has_object_permission(self, request, view, obj):
        # Allow read-only access for SAFE methods
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow write only if user is admin or owner
        return request.user.is_staff or obj.owner == request.user


# this permission class allows only authenticated users to access the view
class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == 'vendor'

