from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.security.auth_views import LoginAPIView, LogoutAPIView, RefreshAPIView
from apps.security.views import (
    PermissionViewSet,
    ProfileAPIView,
    RolePermissionViewSet,
    RoleViewSet,
    UserRoleViewSet,
    UserViewSet,
    user_permissions_view,
)

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name="token_obtain_pair_v1"),
    path("auth/logout/", LogoutAPIView.as_view(), name="token_blacklist_v1"),
    path("auth/permissions/", user_permissions_view, name="auth-permissions-v1"),
    path("auth/profile/", ProfileAPIView.as_view(), name="auth-profile-v1"),
    path("auth/refresh/", RefreshAPIView.as_view(), name="token_refresh_v1"),
]

router = SimpleRouter(use_regex_path=False)
router.register("users", UserViewSet, basename="user")
router.register("roles", RoleViewSet, basename="role")
router.register("permissions", PermissionViewSet, basename="permission")
router.register("user-roles", UserRoleViewSet, basename="userrole")
router.register("role-users", UserRoleViewSet, basename="role-user")
router.register("role-permissions", RolePermissionViewSet, basename="rolepermission")
router.register("resources", PermissionViewSet, basename="resource")
router.register("resource-roles", RolePermissionViewSet, basename="resource-role")

urlpatterns += router.urls
