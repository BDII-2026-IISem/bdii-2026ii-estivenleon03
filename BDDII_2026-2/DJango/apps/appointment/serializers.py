from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from .models import Appointment
from apps.patient.models import Pet
from apps.staff.models import Veterinarian
from apps.patient.serializers import PetSerializer
from apps.staff.serializers import VeterinarianSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    pet_details = PetSerializer(source='pet', read_only=True)
    veterinarian_details = VeterinarianSerializer(source='veterinarian', read_only=True)
    status = serializers.ChoiceField(
        choices=Appointment.StatusChoices.choices,
        required=False,
        default=Appointment.StatusChoices.SCHEDULED,
        error_messages={
            'invalid_choice': (
                'Invalid appointment status. Choose SCHEDULED, CONFIRMED, '
                'IN_CONSULTATION, COMPLETED, or CANCELLED.'
            ),
        },
    )

    ACTIVE_STATUSES = (
        Appointment.StatusChoices.SCHEDULED,
        Appointment.StatusChoices.CONFIRMED,
        Appointment.StatusChoices.IN_CONSULTATION,
    )

    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance
        pet = attrs.get('pet', instance.pet if instance else None)
        veterinarian = attrs.get(
            'veterinarian',
            instance.veterinarian if instance else None,
        )
        start_time = attrs.get(
            'start_time',
            instance.start_time if instance else None,
        )
        end_time = attrs.get('end_time', instance.end_time if instance else None)
        status_value = attrs.get(
            'status',
            instance.status if instance else Appointment.StatusChoices.SCHEDULED,
        )
        is_active = attrs.get('is_active', instance.is_active if instance else True)

        errors = self._schedule_errors(
            pet,
            veterinarian,
            start_time,
            end_time,
            status_value,
            is_active,
            validate_pet=('pet' in attrs or instance is None),
            validate_veterinarian=(
                'veterinarian' in attrs or instance is None
            ),
            exclude_pk=instance.pk if instance else None,
        )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    @classmethod
    def _schedule_errors(
        cls, pet, veterinarian, start_time, end_time, status_value, is_active,
        validate_pet=True, validate_veterinarian=True, exclude_pk=None,
    ):
        errors = {}
        if validate_pet and pet is not None and not pet.is_active:
            errors['pet'] = 'Select an active pet.'
        if (
            validate_veterinarian
            and veterinarian is not None
            and not veterinarian.is_active
        ):
            errors['veterinarian'] = 'Select an active veterinarian.'
        if start_time is not None and end_time is not None and end_time <= start_time:
            errors['end_time'] = 'Appointment end time must be after its start time.'

        if (
            errors
            or not is_active
            or status_value not in cls.ACTIVE_STATUSES
            or pet is None
            or veterinarian is None
            or start_time is None
            or end_time is None
        ):
            return errors

        overlaps = Appointment.objects.filter(
            is_active=True,
            status__in=cls.ACTIVE_STATUSES,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).filter(Q(pet=pet) | Q(veterinarian=veterinarian))
        if exclude_pk is not None:
            overlaps = overlaps.exclude(pk=exclude_pk)
        if overlaps.exists():
            errors['non_field_errors'] = (
                'This time overlaps an active appointment for the selected pet '
                'or veterinarian.'
            )
        return errors

    @staticmethod
    def _lock_participants(pets, veterinarians):
        locked_pets = {
            pet.pk: pet
            for pet in Pet.objects.select_for_update()
            .filter(pk__in=sorted({item.pk for item in pets if item is not None}))
            .order_by('pk')
        }
        locked_veterinarians = {
            veterinarian.pk: veterinarian
            for veterinarian in Veterinarian.objects.select_for_update()
            .filter(
                pk__in=sorted(
                    {item.pk for item in veterinarians if item is not None}
                )
            )
            .order_by('pk')
        }
        return locked_pets, locked_veterinarians

    def _save_with_locked_participants(self, validated_data, *, creating):
        instance = self.instance
        requested_pet = validated_data.get(
            'pet', instance.pet if instance else None
        )
        requested_veterinarian = validated_data.get(
            'veterinarian', instance.veterinarian if instance else None
        )
        pets = [requested_pet]
        veterinarians = [requested_veterinarian]
        if instance:
            pets.append(instance.pet)
            veterinarians.append(instance.veterinarian)

        locked_pets, locked_veterinarians = self._lock_participants(
            pets, veterinarians
        )
        pet = locked_pets.get(requested_pet.pk)
        veterinarian = locked_veterinarians.get(requested_veterinarian.pk)
        validated_data['pet'] = pet
        validated_data['veterinarian'] = veterinarian

        start_time = validated_data.get(
            'start_time', instance.start_time if instance else None
        )
        end_time = validated_data.get(
            'end_time', instance.end_time if instance else None
        )
        status_value = validated_data.get(
            'status',
            instance.status if instance else Appointment.StatusChoices.SCHEDULED,
        )
        is_active = validated_data.get(
            'is_active', instance.is_active if instance else True
        )
        errors = self._schedule_errors(
            pet,
            veterinarian,
            start_time,
            end_time,
            status_value,
            is_active,
            validate_pet=('pet' in validated_data or instance is None),
            validate_veterinarian=(
                'veterinarian' in validated_data or instance is None
            ),
            exclude_pk=instance.pk if instance else None,
        )
        if errors:
            raise serializers.ValidationError(errors)

        if creating:
            return super().create(validated_data)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        with transaction.atomic():
            return self._save_with_locked_participants(
                validated_data, creating=True
            )

    def update(self, instance, validated_data):
        with transaction.atomic():
            return self._save_with_locked_participants(
                validated_data, creating=False
            )
