from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.patient.models import Owner
from apps.patient.serializers import OwnerStatusField


class ClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=2, max_length=120)
    docType = serializers.CharField(source="doc_type", required=False, default="CC")
    docNumber = serializers.CharField(
        source="doc_number",
        max_length=30,
        validators=[UniqueValidator(queryset=Owner.objects.all())],
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=120,
    )
    address = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
    )
    status = OwnerStatusField(source="is_active", required=False, default=False)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Owner
        fields = (
            "id",
            "name",
            "docType",
            "docNumber",
            "phone",
            "email",
            "address",
            "status",
            "createdAt",
            "updatedAt",
        )
        read_only_fields = ("id", "createdAt", "updatedAt")

    def validate_email(self, value):
        if value:
            matches = Owner.objects.filter(email__iexact=value)
            if self.instance:
                matches = matches.exclude(pk=self.instance.pk)
            if matches.exists():
                raise serializers.ValidationError(
                    "Un cliente con este correo ya existe."
                )
        return value

