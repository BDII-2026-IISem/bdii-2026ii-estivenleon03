from django.db import models
from apps.common.models import BaseModel

class Owner(BaseModel):
    doc_type = models.CharField(max_length=20)
    doc_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=120, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'owners'
        verbose_name = 'Propietario'
        verbose_name_plural = 'Propietarios'

    def __str__(self):
        return f"{self.name} - {self.doc_number}"


class Pet(BaseModel):
    class GenderChoices(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'

    owner = models.ForeignKey(
        Owner, 
        on_delete=models.RESTRICT, 
        related_name='pets', 
        db_column='owner_id'
    )
    name = models.CharField(max_length=80)
    species = models.CharField(max_length=50, null=True, blank=True)
    breed = models.CharField(max_length=50, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'pets'
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'

    def __str__(self):
        return f"{self.name} ({self.species})"
