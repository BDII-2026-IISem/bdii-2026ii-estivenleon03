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
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly filter = signal('');
  readonly dialogVisible = signal(false);

  readonly form = this.fb.group({
    roleId: [null as number | null, [Validators.required]],
    resourceId: [null as number | null, [Validators.required]],
  });

  readonly resourceOptions = computed(() =>
    this.resources().map((r) => ({ id: r.id, label: `${r.method} ${r.path}` }))
  );

  readonly visibleRows = computed(() =>
    filterRows(this.rows(), this.filter(), (row) => [
      this.roleLabel(row.roleId),
      this.resourceLabel(row.resourceId),
    ])
  );

  constructor() {
    this.load();
    this.rolesApi.list().subscribe({ next: (res) => this.roles.set(res) });
    this.resourcesApi.list().subscribe({ next: (res) => this.resources.set(res) });
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

  resource(id: number | undefined): Resource | undefined {
    return this.resources().find((r) => r.id === id);
  }

  resourceLabel(id: number | undefined): string {
    const res = this.resource(id);
    return res ? `${res.method} ${res.path}` : `#${id}`;
  }

  openCreate(): void {
    this.form.reset({ roleId: null, resourceId: null });
    this.dialogVisible.set(true);
  }

  submit(): void {
    const val = this.form.getRawValue();
    if (!val.roleId || !val.resourceId) {
      this.form.markAllAsTouched();
      return;
    }
    const payload: ResourceRolePayload = {
      roleId: val.roleId,
      resourceId: val.resourceId,
      status: 'active',
    };
    this.saving.set(true);
    this.api.create(payload).subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success('Concesión otorgada');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo conceder', toApiMessage(err));
      },
    });
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
