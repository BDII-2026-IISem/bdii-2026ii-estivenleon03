from django.db import models
from apps.common.models import BaseModel
from apps.patient.models import Pet
from apps.staff.models import Veterinarian
from apps.appointment.models import Appointment

class Consultation(BaseModel):
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.RESTRICT, 
        null=True, 
        blank=True, 
        db_column='appointment_id'
    )
    pet = models.ForeignKey(
        Pet, 
        on_delete=models.RESTRICT, 
        related_name='consultations', 
        db_column='pet_id'
    )
    veterinarian = models.ForeignKey(
        Veterinarian, 
        on_delete=models.RESTRICT, 
        related_name='consultations', 
        db_column='veterinarian_id'
    )
    title = models.CharField(max_length=150, default='General Consultation')
    description = models.TextField(null=True, blank=True)
    temperature_c = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    symptoms = models.TextField()
    diagnosis = models.TextField()

    class Meta:
        db_table = 'consultations'
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'


class Prescription(BaseModel):
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='prescriptions', 
        db_column='consultation_id'
    )
    medication_name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.IntegerField()

    class Meta:
        db_table = 'prescriptions'
        verbose_name = 'Prescripción'
        verbose_name_plural = 'Prescripciones'


class Vaccine(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'vaccines'
        verbose_name = 'Vacuna'
        verbose_name_plural = 'Vacunas'


class VaccineBatch(BaseModel):
    vaccine = models.ForeignKey(
        Vaccine, 
        on_delete=models.RESTRICT, 
        related_name='batches', 
        db_column='vaccine_id'
    )
    name = models.CharField(max_length=100)
    batch_number = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    expiration_date = models.DateField()
    stock_quantity = models.IntegerField(default=0)

    class Meta:
        db_table = 'vaccine_batches'
        verbose_name = 'Lote de Vacuna'
        verbose_name_plural = 'Lotes de Vacunas'


class VaccineApplication(BaseModel):
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.RESTRICT, 
        related_name='vaccine_applications', 
        db_column='consultation_id'
    )
    vaccine_batch = models.ForeignKey(
        VaccineBatch, 
        on_delete=models.RESTRICT, 
        related_name='applications', 
        db_column='vaccine_batch_id'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    dosage_ml = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'vaccine_applications'
        verbose_name = 'Aplicación de Vacuna'
        verbose_name_plural = 'Aplicaciones de Vacunas'
