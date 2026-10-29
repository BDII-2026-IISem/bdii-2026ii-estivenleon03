from django.contrib import admin
from .models import Owner, Pet

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'doc_type', 'doc_number', 'phone', 'email')
    search_fields = ('name', 'doc_number')

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'species', 'breed', 'owner', 'gender')
    search_fields = ('name', 'species')
