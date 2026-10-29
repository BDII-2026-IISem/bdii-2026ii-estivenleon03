from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.security.views import (
    UserViewSet,
    RoleViewSet,
    PermissionViewSet,
    UserRoleViewSet,
    RolePermissionViewSet,
    user_permissions_view,
    user_profile_view,
)
from apps.patient.views import OwnerViewSet, PetViewSet
from apps.staff.views import VeterinarianViewSet
from apps.appointment.views import AppointmentViewSet
from apps.clinical.views import ConsultationViewSet, PrescriptionViewSet, VaccineViewSet, VaccineBatchViewSet, VaccineApplicationViewSet
from apps.billing.views import PaymentViewSet, PaymentAuditViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'user-roles', UserRoleViewSet, basename='userrole')
router.register(r'role-permissions', RolePermissionViewSet, basename='rolepermission')
router.register(r'owners', OwnerViewSet, basename='owner')
router.register(r'pets', PetViewSet, basename='pet')
router.register(r'veterinarians', VeterinarianViewSet, basename='veterinarian')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'consultations', ConsultationViewSet, basename='consultation')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'vaccines', VaccineViewSet, basename='vaccine')
router.register(r'vaccine-batches', VaccineBatchViewSet, basename='vaccinebatch')
router.register(r'vaccine-applications', VaccineApplicationViewSet, basename='vaccineapplication')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'payment-audits', PaymentAuditViewSet, basename='paymentaudit')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Endpoints de la API v1
    path('api/v1/', include(router.urls)),
    
    # Autenticación, Permisos y Perfil bajo /api/v1/auth/
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair_v1'),
    path('api/v1/auth/permissions/', user_permissions_view, name='auth-permissions-v1'),
    path('api/v1/auth/profile/', user_profile_view, name='auth-profile-v1'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh_v1'),

    # Rutas bajo /api/auth/ para compatibilidad
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/permissions/', user_permissions_view, name='auth-permissions'),
    path('api/auth/profile/', user_profile_view, name='auth-profile'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),

    # Documentación Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Fallback Directo de Tokens
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair_direct'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_direct'),
]
