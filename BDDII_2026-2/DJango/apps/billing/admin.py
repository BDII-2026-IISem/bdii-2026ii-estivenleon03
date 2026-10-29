from django.contrib import admin
from .models import Payment, PaymentAudit

admin.site.register(Payment)
admin.site.register(PaymentAudit)
