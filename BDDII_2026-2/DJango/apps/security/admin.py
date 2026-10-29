from django.contrib import admin
from .models import User, Role, Permission, UserRole, RolePermission

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'is_active', 'created_at')
    search_fields = ('name', 'email')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'http_method')

admin.site.register(UserRole)
admin.site.register(RolePermission)
