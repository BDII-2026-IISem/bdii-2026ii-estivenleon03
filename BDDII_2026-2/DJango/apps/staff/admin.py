from django.contrib import admin
from .models import Veterinarian

@admin.register(Veterinarian)
class VeterinarianAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'license_number', 'user')
    search_fields = ('name', 'license_number')
