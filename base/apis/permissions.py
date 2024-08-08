from rest_framework import permissions
from rest_framework.permissions import BasePermission

class isAdminOrReadonly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user and request.user.is_staff)
            
            
        