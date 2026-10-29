from django.contrib import admin
from .models import Consultation, Prescription, Vaccine, VaccineBatch, VaccineApplication

admin.site.register(Consultation)
admin.site.register(Prescription)
admin.site.register(Vaccine)
admin.site.register(VaccineBatch)
admin.site.register(VaccineApplication)
