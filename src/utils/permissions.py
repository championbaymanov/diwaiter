from rest_framework.permissions import BasePermission


class IsSuperAdminUser(BasePermission):
    def has_permission(self, request, view):
        return True if bool(
            request.user and request.user.is_authenticated and request.user.profile.permission == 0) else False


class IsAdminUserCustom(BasePermission):
    def has_permission(self, request, view):
        return True if bool(
            request.user and request.user.is_authenticated and request.user.profile.permission <= 1) else False


class IsManagerUser(BasePermission):

    def has_permission(self, request, view):
        get = request.method == 'GET'
        return True if bool(
            request.user and request.user.is_authenticated and request.user.profile.permission <= 2) or get else False

    def has_object_permission(self, request, view, obj):
        get = request.method == 'GET'
        return True if get or request.user.is_superuser or request.user.profile.permission <= 2 else False


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return True if bool(request.user and request.user.is_authenticated) else False


class IsAnyAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return True

    # def has_object_permission(self, request, view, obj):
    #     if request.method == 'GET' or obj.user.pk == request.user.pk:
    #         return True
    #     return False
