from django.contrib.auth.hashers import check_password, make_password
from django.core.validators import MinLengthValidator
from django.db import models
from apps.common.models import BaseModel


class Owner(BaseModel):
    doc_type = models.CharField(max_length=20)
    doc_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120, validators=[MinLengthValidator(2)])
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=120, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'owners'
        verbose_name = 'Propietario'
        verbose_name_plural = 'Propietarios'
        constraints = [
            models.UniqueConstraint(fields=("email",), name="uq_owners_email"),
        ]
        indexes = [
            models.Index(fields=("is_active",), name="ix_owners_status"),
        ]

    def __str__(self):
        return f"{self.name} - {self.doc_number}"

    def save(self, *args, **kwargs):
        if self.email is not None:
            self.email = self.email.strip().lower() or None
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return bool(self.password) and check_password(raw_password, self.password)


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
