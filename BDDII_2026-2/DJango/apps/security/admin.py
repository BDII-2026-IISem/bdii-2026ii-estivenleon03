from django.contrib import admin
from .models import RefreshToken, User, Role, Permission, UserRole, RolePermission

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


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "family_id", "status", "expires_at")
    list_filter = ("status",)
    search_fields = ("token_hash", "family_id", "user__username")
    readonly_fields = ("token_hash", "family_id")
