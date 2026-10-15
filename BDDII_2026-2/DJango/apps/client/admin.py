from django.contrib import admin
from apps.client.models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "address", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "email", "phone", "address")
    list_editable = ("status",)
    ordering = ("name", "email")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Información del cliente", {"fields": ("name", "email", "phone", "address")}),
        ("Estado", {"fields": ("status",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
