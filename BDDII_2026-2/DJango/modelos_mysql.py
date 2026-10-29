# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Appointments(models.Model):
    pet = models.ForeignKey('Pets', models.DO_NOTHING)
    veterinarian = models.ForeignKey('Veterinarians', models.DO_NOTHING)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'appointments'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Consultations(models.Model):
    appointment = models.OneToOneField(Appointments, models.DO_NOTHING, blank=True, null=True)
    pet = models.ForeignKey('Pets', models.DO_NOTHING)
    veterinarian = models.ForeignKey('Veterinarians', models.DO_NOTHING)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    temperature_c = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    heart_rate = models.IntegerField(blank=True, null=True)
    symptoms = models.TextField()
    diagnosis = models.TextField()
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consultations'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Owners(models.Model):
    doc_type = models.CharField(max_length=20)
    doc_number = models.CharField(unique=True, max_length=30)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=120, blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'owners'


class Payments(models.Model):
    appointment = models.ForeignKey(Appointments, models.DO_NOTHING)
    reference_type = models.CharField(max_length=50)
    reference_id = models.IntegerField()
    method = models.CharField(max_length=11)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments'


class PaymentsAudit(models.Model):
    id = models.BigAutoField(primary_key=True)
    payment_id = models.IntegerField()
    actionsale = models.CharField(db_column='actionSale', max_length=6)  # Field name made lowercase.
    changed_at = models.DateTimeField()
    changed_by = models.CharField(max_length=255)
    before_data = models.JSONField(blank=True, null=True)
    after_data = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments_audit'


class Permissions(models.Model):
    resource = models.CharField(max_length=100)
    http_method = models.CharField(max_length=10)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permissions'


class Pets(models.Model):
    owner = models.ForeignKey(Owners, models.DO_NOTHING)
    name = models.CharField(max_length=80)
    species = models.CharField(max_length=50, blank=True, null=True)
    breed = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=6, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pets'


class Prescriptions(models.Model):
    consultation = models.ForeignKey(Consultations, models.DO_NOTHING)
    medication_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prescriptions'


class RolePermissions(models.Model):
    role = models.OneToOneField('Roles', models.DO_NOTHING, primary_key=True)  # The composite primary key (role_id, permission_id) found, that is not supported. The first column is selected.
    permission = models.ForeignKey(Permissions, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'role_permissions'
        unique_together = (('role', 'permission'),)


class Roles(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles'


class UserRoles(models.Model):
    user = models.OneToOneField('Users', models.DO_NOTHING, primary_key=True)  # The composite primary key (user_id, role_id) found, that is not supported. The first column is selected.
    role = models.ForeignKey(Roles, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_roles'
        unique_together = (('user', 'role'),)


class Users(models.Model):
    name = models.CharField(max_length=120)
    email = models.CharField(unique=True, max_length=120)
    password_hash = models.CharField(max_length=255)
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class VaccineApplications(models.Model):
    consultation = models.ForeignKey(Consultations, models.DO_NOTHING)
    vaccine_batch = models.ForeignKey('VaccineBatches', models.DO_NOTHING)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    dosage_ml = models.DecimalField(max_digits=4, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vaccine_applications'


class VaccineBatches(models.Model):
    vaccine = models.ForeignKey('Vaccines', models.DO_NOTHING)
    name = models.CharField(max_length=100)
    batch_number = models.CharField(unique=True, max_length=50)
    description = models.TextField(blank=True, null=True)
    expiration_date = models.DateField()
    stock_quantity = models.IntegerField()
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vaccine_batches'


class Vaccines(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vaccines'


class Veterinarians(models.Model):
    user = models.OneToOneField(Users, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=120)
    license_number = models.CharField(unique=True, max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veterinarians'
