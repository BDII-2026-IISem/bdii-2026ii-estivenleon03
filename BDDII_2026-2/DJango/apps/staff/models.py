from django.db import models
from apps.common.models import BaseModel
from apps.security.models import User

class Veterinarian(BaseModel):
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='user_id'
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
