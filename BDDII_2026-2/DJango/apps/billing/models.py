from django.db import models
from apps.appointment.models import Appointment

class Payment(models.Model):
    class MethodChoices(models.TextChoices):
        CASH = 'CASH', 'Cash'
        DEBIT_CARD = 'DEBIT_CARD', 'Debit Card'
        CREDIT_CARD = 'CREDIT_CARD', 'Credit Card'
        TRANSFER = 'TRANSFER', 'Transfer'

    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        CANCELLED = 'CANCELLED', 'Cancelled'

    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.RESTRICT, 
        related_name='payments', 
        db_column='appointment_id'
    )
    reference_type = models.CharField(max_length=50, default='APPOINTMENT')
    reference_id = models.IntegerField()
    method = models.CharField(max_length=20, choices=MethodChoices.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PAID)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'


class PaymentAudit(models.Model):
    class ActionChoices(models.TextChoices):
        UPDATE = 'UPDATE', 'Update'
        DELETE = 'DELETE', 'Delete'
        INSERT = 'INSERT', 'Insert'

    id = models.BigAutoField(primary_key=True)
    payment_id = models.IntegerField()
    actionSale = models.CharField(max_length=10, choices=ActionChoices.choices, default=ActionChoices.INSERT)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.CharField(max_length=255, default='Admin')
    before_data = models.JSONField(null=True, blank=True)
    after_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'payments_audit'
        verbose_name = 'Auditoría de Pago'
        verbose_name_plural = 'Auditorías de Pagos'
