from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers
from .models import Consultation, Prescription, Vaccine, VaccineBatch, VaccineApplication
from apps.patient.models import Pet
from apps.staff.models import Veterinarian


class ConsultationSerializer(serializers.ModelSerializer):
    pet = serializers.PrimaryKeyRelatedField(
        queryset=Pet.objects.all(),
        required=False,
    )
    veterinarian = serializers.PrimaryKeyRelatedField(
        queryset=Veterinarian.objects.all(),
        required=False,
    )

    class Meta:
        model = Consultation
        fields = '__all__'

    def validate(self, attrs):
        appointment = attrs.get(
            'appointment',
            self.instance.appointment if self.instance else None,
        )
        current_appointment = self.instance.appointment if self.instance else None
        changed_appointment = (
            self.instance is not None
            and 'appointment' in attrs
            and appointment != current_appointment
        )

        pet = attrs.get('pet')
        veterinarian = attrs.get('veterinarian')
        if (
            pet is None
            and self.instance
            and not (changed_appointment and appointment is not None)
        ):
            pet = self.instance.pet
        if (
            veterinarian is None
            and self.instance
            and not (changed_appointment and appointment is not None)
        ):
            veterinarian = self.instance.veterinarian

        errors = {}
        if appointment is not None:
            if pet is not None and pet.pk != appointment.pet_id:
                errors['pet'] = 'Pet must match the selected appointment.'
            if (
                veterinarian is not None
                and veterinarian.pk != appointment.veterinarian_id
            ):
                errors['veterinarian'] = (
                    'Veterinarian must match the selected appointment.'
                )
            attrs['pet'] = appointment.pet
            attrs['veterinarian'] = appointment.veterinarian
        else:
            if pet is None:
                errors['pet'] = 'A pet is required for a standalone consultation.'
            if veterinarian is None:
                errors['veterinarian'] = (
                    'A veterinarian is required for a standalone consultation.'
                )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class PrescriptionSerializer(serializers.ModelSerializer):
    dosage = serializers.CharField(max_length=100, trim_whitespace=True)
    duration_days = serializers.IntegerField(min_value=1)

    class Meta:
        model = Prescription
        fields = '__all__'

    def validate_dosage(self, value):
        if not value.strip():
            raise serializers.ValidationError('Dosage must not be blank.')
        return value


class VaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = '__all__'


class VaccineBatchSerializer(serializers.ModelSerializer):
    stock_quantity = serializers.IntegerField(
        min_value=0,
        required=False,
        default=0,
    )

    class Meta:
        model = VaccineBatch
        fields = '__all__'


class VaccineApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineApplication
        fields = '__all__'

    def validate_vaccine_batch(self, batch):
        self._validate_batch(batch)
        return batch

    @staticmethod
    def _validate_batch(batch):
        if not batch.is_active:
            raise serializers.ValidationError(
                'Cannot apply a vaccine from an inactive batch.'
            )
        if batch.expiration_date < timezone.localdate():
            raise serializers.ValidationError(
                'Cannot apply a vaccine from an expired batch.'
            )
        if batch.stock_quantity < 1:
            raise serializers.ValidationError(
                'The selected vaccine batch has no doses in stock.'
            )

    def create(self, validated_data):
        with transaction.atomic():
            batch = (
                VaccineBatch.objects.select_for_update()
                .get(pk=validated_data['vaccine_batch'].pk)
            )
            self._validate_batch(batch)
            updated = VaccineBatch.objects.filter(
                pk=batch.pk,
                is_active=True,
                expiration_date__gte=timezone.localdate(),
                stock_quantity__gt=0,
            ).update(
                stock_quantity=F('stock_quantity') - 1,
                updated_at=timezone.now(),
            )
            if not updated:
                raise serializers.ValidationError(
                    {'vaccine_batch': 'The selected batch is no longer available.'}
                )
            validated_data['vaccine_batch'] = batch
            return super().create(validated_data)
