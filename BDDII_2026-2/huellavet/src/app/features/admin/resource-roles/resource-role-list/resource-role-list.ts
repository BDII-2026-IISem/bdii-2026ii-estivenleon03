import { Component, computed, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ConfirmationService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { SelectModule } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { forkJoin } from 'rxjs';
import { catchError, concatMap, finalize, map, of, toArray } from 'rxjs';
import { Resource } from '../../../../core/models/resource.model';
import { ResourceRole, ResourceRolePayload } from '../../../../core/models/resource-role.model';
import { Role } from '../../../../core/models/role.model';
import { NotificationService } from '../../../../core/services/notification.service';
import { toApiMessage } from '../../../../core/utils/to-api-message';
import { filterRows } from '../../../../core/utils/filter-rows';
import { methodSeverity } from '../../../../core/utils/http-method';
import { EmptyState } from '../../../../shared/ui/empty-state/empty-state';
import { PageHeader } from '../../../../shared/ui/page-header/page-header';
import { StatusTag } from '../../../../shared/ui/status-tag/status-tag';
import { HasPermission } from '../../../../shared/directives/has-permission';
import { ResourceApi } from '../../resources/resource-api';
import { RoleApi } from '../../roles/role-api';
import { ResourceRoleApi } from '../resource-role-api';

interface ResourceOption {
  id: number;
  path: string;
  resourceName: string;
  actionLabel: string;
  method: Resource['method'];
  severity: ReturnType<typeof methodSeverity>;
}

type GrantResult =
  | { resourceId: number; success: true }
  | { resourceId: number; success: false; error: unknown };

@Component({
  selector: 'app-resource-role-list',
  standalone: true,
  imports: [
    ButtonModule,
    DialogModule,
    EmptyState,
    HasPermission,
    InputTextModule,
    MessageModule,
    PageHeader,
    ReactiveFormsModule,
    SelectModule,
    StatusTag,
    TableModule,
    TagModule,
    TooltipModule,
  ],
  templateUrl: './resource-role-list.html',
  styleUrl: './resource-role-list.css',
  host: { class: 'block' },
})
export class ResourceRoleList {
  private readonly api = inject(ResourceRoleApi);
  private readonly rolesApi = inject(RoleApi);
  private readonly resourcesApi = inject(ResourceApi);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);
  private readonly fb = inject(NonNullableFormBuilder);

  readonly methodSeverity = methodSeverity;
  readonly rows = signal<ResourceRole[]>([]);
  readonly roles = signal<Role[]>([]);
  readonly resources = signal<Resource[]>([]);
  readonly loading = signal(true);
  readonly optionsLoading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly optionsError = signal<string | null>(null);
  readonly filter = signal('');
  readonly permissionFilter = signal('');
  readonly selectedResourceIds = signal<number[]>([]);
  readonly selectedRoleId = signal<number | null>(null);
  readonly selectionTouched = signal(false);
  readonly dialogVisible = signal(false);

  readonly form = this.fb.group({
    roleId: [null as number | null, [Validators.required]],
  });

  readonly resourceOptions = computed<ResourceOption[]>(() =>
    this.resources()
      .filter((resource) => resource.status === 'active')
      .map((resource) => ({
        id: resource.id,
        path: this.normalizePath(resource.path),
        resourceName: this.resourceName(resource.path),
        actionLabel: this.actionLabel(resource.method),
        method: resource.method,
        severity: this.methodSeverity(resource.method),
      }))
  );

  readonly visibleRows = computed(() =>
    filterRows(this.rows(), this.filter(), (row) => [
      this.roleLabel(row.roleId),
      this.resourceLabel(row.resourceId),
      this.actionLabel(this.resource(row.resourceId)?.method),
      this.resourceName(this.resource(row.resourceId)?.path ?? ''),
    ])
  );

  readonly selectableResources = computed(() => {
    const roleId = this.selectedRoleId();
    if (roleId === null) return [];
    const query = this.permissionFilter().trim().toLowerCase();
    return this.resourceOptions().filter((option) => {
      const alreadyGranted = this.existingGrant(roleId, option.id)?.status === 'active';
      const matchesQuery =
        !query ||
        `${option.actionLabel} ${option.resourceName} ${option.path} ${option.method}`
          .toLowerCase()
          .includes(query);
      return !alreadyGranted && matchesQuery;
    });
  });

  constructor() {
    this.load();
    forkJoin({
      roles: this.rolesApi.list(),
      resources: this.resourcesApi.list(),
    })
      .pipe(finalize(() => this.optionsLoading.set(false)))
      .subscribe({
        next: ({ roles, resources }) => {
          this.roles.set(roles);
          this.resources.set(resources);
        },
        error: (err: unknown) => this.optionsError.set(toApiMessage(err)),
      });
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.list().subscribe({
      next: (data) => {
        this.rows.set(data);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.rows.set([]);
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }

  roleLabel(id: number | undefined): string {
    return this.roles().find((r) => r.id === id)?.name ?? `#${id}`;
  }

  roleDescription(id: number | undefined): string | null {
    return this.roles().find((role) => role.id === id)?.description ?? null;
  }

  resource(id: number | undefined): Resource | undefined {
    return this.resources().find((r) => r.id === id);
  }

  resourceLabel(id: number | undefined): string {
    const option = this.resourceOptions().find((item) => item.id === id);
    return option ? `${option.actionLabel} · ${option.resourceName}` : `#${id}`;
  }

  roleFor(id: number | null): Role | undefined {
    return this.roles().find((item) => item.id === id);
  }

  actionLabel(method?: Resource['method']): string {
    switch (method) {
      case 'GET':
        return 'Consultar';
      case 'POST':
        return 'Crear o registrar';
      case 'PUT':
      case 'PATCH':
        return 'Editar';
      case 'DELETE':
        return 'Eliminar o retirar';
      default:
        return 'Acción';
    }
  }

  actionDescription(method?: Resource['method']): string {
    switch (method) {
      case 'GET':
        return 'Permite ver la información de este recurso.';
      case 'POST':
        return 'Permite crear registros o realizar esta operación.';
      case 'PUT':
      case 'PATCH':
        return 'Permite modificar la información de este recurso.';
      case 'DELETE':
        return 'Permite eliminar o retirar el recurso, según la operación configurada.';
      default:
        return '';
    }
  }

  resourceName(path: string): string {
    const segments = this.normalizePath(path)
      .replace(/^\/api\/v1\/?/, '')
      .split('/')
      .filter(Boolean);
    const collection = segments[0] ?? '';
    const names: Record<string, string> = {
      users: 'Usuarios',
      roles: 'Roles',
      permissions: 'Recursos y permisos',
      'user-roles': 'Asignaciones de roles',
      'role-permissions': 'Permisos por rol',
      owners: 'Propietarios',
      pets: 'Mascotas',
      veterinarians: 'Veterinarios',
      appointments: 'Citas',
      consultations: 'Consultas',
      prescriptions: 'Prescripciones',
      vaccines: 'Vacunas',
      'vaccine-batches': 'Lotes de vacunas',
      'vaccine-applications': 'Aplicaciones de vacunas',
      'product-types': 'Tipos de producto',
      products: 'Productos e inventario',
      sales: 'Ventas',
      payments: 'Pagos de citas',
      'payment-audits': 'Auditoría de pagos',
    };
    const baseName =
      names[collection] ??
      collection.replace(/-/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());

    if (segments[1] === 'available') return `${baseName} disponibles`;
    if (segments[1] === ':id' && segments[2] === 'payments') return 'Abonos de ventas';
    return baseName || 'Recurso';
  }

  private normalizePath(path: string): string {
    return `/${path}`.replace(/\/+/g, '/').replace(/\/$/, '') || '/';
  }

  openCreate(): void {
    this.form.reset({ roleId: null });
    this.selectedRoleId.set(null);
    this.permissionFilter.set('');
    this.selectedResourceIds.set([]);
    this.selectionTouched.set(false);
    this.dialogVisible.set(true);
  }

  onRoleChange(): void {
    this.selectedRoleId.set(this.form.controls.roleId.value);
    this.selectedResourceIds.set([]);
    this.selectionTouched.set(false);
  }

  submit(): void {
    const val = this.form.getRawValue();
    const selectedIds = this.selectedResourceIds();
    if (!val.roleId || selectedIds.length === 0) {
      this.form.markAllAsTouched();
      this.selectionTouched.set(true);
      return;
    }

    this.saving.set(true);
    of(...selectedIds)
      .pipe(
        concatMap((resourceId) => {
          const payload: ResourceRolePayload = {
            roleId: val.roleId!,
            resourceId,
            status: 'active',
          };
          const existing = this.existingGrant(val.roleId, resourceId);
          const request = existing
            ? this.api.update(existing.id, payload)
            : this.api.create(payload);
          return request.pipe(
            map((): GrantResult => ({ resourceId, success: true })),
            catchError((error: unknown) => of({ resourceId, success: false, error }))
          );
        }),
        toArray(),
        finalize(() => this.saving.set(false))
      )
      .subscribe((results) => {
        const failures = results.filter(
          (result): result is Extract<GrantResult, { success: false }> => !result.success
        );
        const granted = results.length - failures.length;
        const failedIds = failures.map((result) => result.resourceId);

        if (granted > 0) {
          this.load();
        }

        if (failures.length === 0) {
          this.notify.success(
            granted === 1 ? 'Se concedió 1 permiso' : `Se concedieron ${granted} permisos`
          );
          this.dialogVisible.set(false);
          this.selectedResourceIds.set([]);
          return;
        }

        this.selectedResourceIds.set(failedIds);
        const failedNames = failures
          .map(({ resourceId, error }) =>
            `${this.resourceLabel(resourceId)}: ${toApiMessage(error)}`
          )
          .join(', ');
        const detail = `${granted} concedido(s), ${failures.length} fallido(s). ${failedNames}`;
        if (granted > 0) {
          this.notify.warn('Asignación parcial', detail);
        } else {
          this.notify.error('No se pudieron conceder los permisos', detail);
        }
      });
  }

  isSelected(resourceId: number): boolean {
    return this.selectedResourceIds().includes(resourceId);
  }

  toggleResource(resourceId: number, event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.selectionTouched.set(true);
    this.selectedResourceIds.update((selected) =>
      checked
        ? [...new Set([...selected, resourceId])]
        : selected.filter((id) => id !== resourceId)
    );
  }

  toggleVisibleResources(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    const visibleIds = this.selectableResources().map((option) => option.id);
    this.selectionTouched.set(true);
    this.selectedResourceIds.update((selected) =>
      checked
        ? [...new Set([...selected, ...visibleIds])]
        : selected.filter((id) => !visibleIds.includes(id))
    );
  }

  existingGrant(roleId: number | null, resourceId: number): ResourceRole | undefined {
    if (roleId === null) return undefined;
    return this.rows().find((row) => {
      const rowRoleId = row.roleId ?? row.role_id ??
        (typeof row.role === 'object' ? row.role.id : row.role);
      const rowResourceId = row.resourceId ?? row.permission_id ??
        (typeof row.permission === 'object' ? row.permission.id : row.permission);
      return rowRoleId === roleId && rowResourceId === resourceId;
    });
  }

  allVisibleSelected(): boolean {
    const visibleIds = this.selectableResources().map((option) => option.id);
    return visibleIds.length > 0 && visibleIds.every((id) => this.isSelected(id));
  }

  remove(row: ResourceRole): void {
    this.confirmation.confirm({
      header: 'Retirar concesión',
      message: `¿Retirar el permiso «${this.resourceLabel(row.resourceId)}» al rol «${this.roleLabel(row.roleId)}»?`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Retirar',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.remove(row.id).subscribe({
          next: () => {
            this.notify.warn('Concesión retirada');
            this.load();
          },
          error: (err: unknown) => this.notify.error('No se pudo retirar', toApiMessage(err)),
        }),
    });
  }
}
