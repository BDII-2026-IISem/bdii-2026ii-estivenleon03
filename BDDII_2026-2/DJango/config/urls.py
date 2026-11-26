from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import AllowAny

from apps.security.auth_views import LoginAPIView, LogoutAPIView, RefreshAPIView
from apps.security.views import ProfileAPIView, user_permissions_view
from apps.security.urls import router as security_router
from apps.client.urls import router as client_router
from apps.patient.urls import router as patient_router
from apps.staff.urls import router as staff_router
from apps.appointment.urls import router as appointment_router
from apps.clinical.urls import router as clinical_router
from apps.billing.urls import router as billing_router
from apps.product.urls import router as product_router
from apps.sale.urls import router as sale_router

api_root_router = DefaultRouter(use_regex_path=False)
for app_router in (
    security_router,
    patient_router,
    client_router,
    staff_router,
    appointment_router,
    clinical_router,
    product_router,
    sale_router,
    billing_router,
):
    api_root_router.registry.extend(app_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Endpoints de la API v1 organizados por aplicación
    path('api/v1/', api_root_router.get_api_root_view(), name='api-root'),
    path('api/v1/', include('apps.security.urls')),
    path('api/v1/', include('apps.patient.urls')),
    path('api/v1/', include('apps.client.urls')),
    path('api/v1/', include('apps.staff.urls')),
    path('api/v1/', include('apps.appointment.urls')),
    path('api/v1/', include('apps.clinical.urls')),
    path('api/v1/', include('apps.product.urls')),
    path('api/v1/', include('apps.sale.urls')),
    path('api/v1/', include('apps.billing.urls')),
    
    # Autenticación, Permisos y Perfil bajo /api/v1/auth/
    # Rutas bajo /api/auth/ para compatibilidad
    path('api/auth/login/', LoginAPIView.as_view(), name='token_obtain_pair'),
    path('api/auth/logout/', LogoutAPIView.as_view(), name='token_blacklist'),
    path('api/auth/permissions/', user_permissions_view, name='auth-permissions'),
    path('api/auth/profile/', ProfileAPIView.as_view(), name='auth-profile'),
    path('api/auth/refresh/', RefreshAPIView.as_view(), name='auth-refresh'),

    # Documentación Swagger
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]),
        name='swagger-ui',
    ),
    path(
        'api/schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema', permission_classes=[AllowAny]),
        name='redoc',
    ),
    
    # Fallback Directo de Tokens
    path('api/token/', LoginAPIView.as_view(), name='token_obtain_pair_direct'),
    path('api/token/refresh/', RefreshAPIView.as_view(), name='token_refresh_direct'),
]
