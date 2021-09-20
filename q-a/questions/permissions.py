from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    def has_permission(self,request,view):
        is_admin = super().has_permission(request,view)
        return request.method in permissions.SAFE_METHODS or is_admin

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        if request.method in permissions.SAFE_METHODS:
             # SAFE_METHODS - GET, OPTIONS, HEAD
            return True
        return obj.author == request.user         


class UserIsOwnerOrReadonly(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        if request.method in permissions.SAFE_METHODS:
             # SAFE_METHODS - GET, OPTIONS, HEAD
            return True
        return obj.user == request.user 
        
        