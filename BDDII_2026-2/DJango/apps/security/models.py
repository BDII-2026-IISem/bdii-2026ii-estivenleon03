from django.db import models
from apps.common.models import BaseModel

class User(BaseModel):
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=120, unique=True)
    password_hash = models.CharField(max_length=255)

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        app_label = 'security'

    def __str__(self):
        return f"{self.name} ({self.email})"


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        app_label = 'security'

    def __str__(self):
        return self.name


class Permission(models.Model):
    resource = models.CharField(max_length=100)
    http_method = models.CharField(max_length=10)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        app_label = 'security'

    def __str__(self):
        return f"{self.http_method} - {self.resource}"


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')

    class Meta:
        db_table = 'user_roles'
        unique_together = (('user', 'role'),)
        app_label = 'security'


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, db_column='permission_id')

    class Meta:
        db_table = 'role_permissions'
        unique_together = (('role', 'permission'),)
        app_label = 'security'


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
        app_label = 'security'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'
        app_label = 'security'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)
        app_label = 'security'
        


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)
        app_label = 'security'


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
        app_label = 'security'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)
        app_label = 'security'


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)
        app_label = 'security'


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
        app_label = 'security'


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
        app_label = 'security'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)
        app_label = 'security'


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'
        app_label = 'security'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
        app_label = 'security'


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
        app_label = 'security'


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
        app_label = 'security'


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
        app_label = 'security'


class Permissions(models.Model):
    resource = models.CharField(max_length=100)
    http_method = models.CharField(max_length=10)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permissions'
        app_label = 'security'


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
        app_label = 'security'


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
        app_label = 'security'


class RolePermissions(models.Model):
    role = models.OneToOneField('Roles', models.DO_NOTHING, primary_key=True)  # The composite primary key (role_id, permission_id) found, that is not supported. The first column is selected.
    permission = models.ForeignKey(Permissions, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'role_permissions'
        unique_together = (('role', 'permission'),)
        app_label = 'security'


class Roles(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles'
        app_label = 'security'


class UserRoles(models.Model):
    user = models.OneToOneField('Users', models.DO_NOTHING, primary_key=True)  # The composite primary key (user_id, role_id) found, that is not supported. The first column is selected.
    role = models.ForeignKey(Roles, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_roles'
        unique_together = (('user', 'role'),)
        app_label = 'security'


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
        app_label = 'security'


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
        app_label = 'security'


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
        app_label = 'security'


class Vaccines(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vaccines'
        app_label = 'security'


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
        app_label = 'security'
