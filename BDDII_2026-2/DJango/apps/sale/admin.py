from django.contrib import admin
from apps.sale.models import ProductSale, Sale

class ProductSaleInline(admin.TabularInline):
    model = ProductSale
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("product", "quantity", "unit_price", "line_total", "status")
    readonly_fields = ("product", "quantity", "unit_price", "line_total", "status")

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "sale_date",
        "subtotal",
        "tax",
        "discounts",
        "total",
        "status",
    )
    list_filter = ("status", "sale_date")
    search_fields = ("client__name", "client__email")
    ordering = ("-sale_date",)
    date_hierarchy = "sale_date"
    readonly_fields = (
        "client",
        "sale_date",
        "subtotal",
        "tax",
        "discounts",
        "total",
        "status",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        ("Información de la venta", {"fields": ("client", "status")}),
        (
            "Totales",
            {
                "fields": ("subtotal", "tax", "discounts", "total"),
                "classes": ("collapse",),
            },
        ),
        ("Fecha", {"fields": ("sale_date",), "classes": ("collapse",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    inlines = (ProductSaleInline,)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("client")

@admin.register(ProductSale)
class ProductSaleAdmin(admin.ModelAdmin):
    list_display = ("sale", "product", "quantity", "unit_price", "line_total", "status")
    list_filter = ("status", "sale__sale_date", "product__status")
    search_fields = ("sale__client__name", "product__name")
    ordering = ("-sale__sale_date", "id")
    readonly_fields = (
        "sale",
        "product",
        "quantity",
        "unit_price",
        "line_total",
        "status",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        ("Línea", {"fields": ("sale", "product", "quantity", "unit_price", "line_total")}),
        ("Estado", {"fields": ("status",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "sale", "sale__client", "product"
        )
