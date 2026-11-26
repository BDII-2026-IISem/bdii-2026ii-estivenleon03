from apps.patient.models import Owner


class Client(Owner):
    class Meta:
        proxy = True
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
