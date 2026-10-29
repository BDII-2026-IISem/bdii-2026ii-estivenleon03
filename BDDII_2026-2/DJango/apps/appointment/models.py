from django.db import models
from apps.common.models import BaseModel
from apps.patient.models import Pet
from apps.staff.models import Veterinarian

class Appointment(BaseModel):
    class StatusChoices(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        IN_CONSULTATION = 'IN_CONSULTATION', 'In Consultation'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    pet = models.ForeignKey(
        Pet, 
        on_delete=models.RESTRICT, 
        related_name='appointments', 
        db_column='pet_id'
    )
    veterinarian = models.ForeignKey(
        Veterinarian, 
        on_delete=models.RESTRICT, 
        related_name='appointments', 
        db_column='veterinarian_id'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.SCHEDULED)

    class Meta:
        db_table = 'appointments'
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'

    def __str__(self):
        return f"Cita #{self.id} - {self.pet.name} ({self.status})"
