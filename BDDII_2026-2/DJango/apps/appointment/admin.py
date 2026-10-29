from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet', 'veterinarian', 'start_time', 'status')
    list_filter = ('status',)
