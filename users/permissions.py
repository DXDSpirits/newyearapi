from rest_framework import permissions


class IsSelfOrIsNew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in ['POST', 'HEAD', 'OPTIONS'] or request.user and request.user.is_authenticated()
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return request.user == obj.owner
        elif hasattr(obj, 'user'):
            return request.user == obj.user
        else:
            return False
