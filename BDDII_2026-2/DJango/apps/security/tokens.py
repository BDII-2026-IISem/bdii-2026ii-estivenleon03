import hashlib
import secrets
import uuid

from django.db import transaction
from django.utils import timezone

from apps.common.status import RecordStatus
from apps.security.models import RefreshToken


class RefreshTokenError(Exception):
    pass


def generate_refresh_value():
    return secrets.token_urlsafe(48)


def hash_token(raw_token):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_refresh_token(user, device_info="", family_id=None):
    value = generate_refresh_value()
    record = RefreshToken.objects.create(
        user=user,
        token_hash=hash_token(value),
        device_info=device_info[:255],
        family_id=family_id or uuid.uuid4().hex,
    )
    return value, record


def rotate_refresh(raw_token):
    error = None
    result = None
    with transaction.atomic():
        record = (
            RefreshToken.objects.select_for_update()
            .filter(token_hash=hash_token(raw_token))
            .first()
        )
        if record is None:
            error = "Refresh token desconocido."
        elif record.status != RecordStatus.ACTIVE:
            RefreshToken.objects.filter(
                family_id=record.family_id,
                status=RecordStatus.ACTIVE,
            ).update(status=RecordStatus.INACTIVE)
            error = "Refresh token reutilizado; familia revocada."
        elif record.expires_at <= timezone.now():
            record.status = RecordStatus.INACTIVE
            record.save(update_fields=("status",))
            error = "Refresh token vencido."
        else:
            record.status = RecordStatus.INACTIVE
            record.save(update_fields=("status",))
            result = create_refresh_token(
                record.user,
                device_info=record.device_info,
                family_id=record.family_id,
            )
    if error:
        raise RefreshTokenError(error)
    return result


def revoke_refresh(raw_token):
    with transaction.atomic():
        record = (
            RefreshToken.objects.select_for_update()
            .filter(token_hash=hash_token(raw_token))
            .first()
        )
        if record is None or record.status != RecordStatus.ACTIVE:
            if record is not None:
                RefreshToken.objects.filter(
                    family_id=record.family_id,
                    status=RecordStatus.ACTIVE,
                ).update(status=RecordStatus.INACTIVE)
            return False
        record.status = RecordStatus.INACTIVE
        record.save(update_fields=("status",))
        return True
