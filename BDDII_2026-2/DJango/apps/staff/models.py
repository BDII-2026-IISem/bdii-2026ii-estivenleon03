from django.db import models
from django.conf import settings
from apps.common.models import BaseModel
from apps.security.models import User

class Veterinarian(BaseModel):
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='user_id',
        related_name='legacy_veterinarian_profile',
    )
    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='auth_user_id',
        related_name='veterinarian_profile',
    )
    name = models.CharField(max_length=120)
    license_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'veterinarians'
        verbose_name = 'Veterinario'
        verbose_name_plural = 'Veterinarios'

    def __str__(self):
        return f"Dr(a). {self.name} - Lic: {self.license_number}"
