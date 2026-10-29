import { Component, computed, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ConfirmationService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { SelectModule } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { TooltipModule } from 'primeng/tooltip';
import { Role } from '../../../../core/models/role.model';
import { RoleUser, RoleUserPayload } from '../../../../core/models/role-user.model';
import { User } from '../../../../core/models/user.model';
import { NotificationService } from '../../../../core/services/notification.service';
import { toApiMessage } from '../../../../core/utils/to-api-message';
import { filterRows } from '../../../../core/utils/filter-rows';
import { EmptyState } from '../../../../shared/ui/empty-state/empty-state';
import { PageHeader } from '../../../../shared/ui/page-header/page-header';
import { StatusTag } from '../../../../shared/ui/status-tag/status-tag';
import { HasPermission } from '../../../../shared/directives/has-permission';
import { UserApi } from '../../users/user-api';
import { RoleApi } from '../../roles/role-api';
import { RoleUserApi } from '../role-user-api';

@Component({
  selector: 'app-role-user-list',
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
    TooltipModule,
  ],
  templateUrl: './role-user-list.html',
  styleUrl: './role-user-list.css',
  host: { class: 'block' },
})
export class RoleUserList {
  private readonly api = inject(RoleUserApi);
  private readonly usersApi = inject(UserApi);
  private readonly rolesApi = inject(RoleApi);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);
  private readonly fb = inject(NonNullableFormBuilder);

  readonly rows = signal<RoleUser[]>([]);
  readonly users = signal<User[]>([]);
  readonly roles = signal<Role[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly filter = signal('');
  readonly dialogVisible = signal(false);

  readonly form = this.fb.group({
    userId: [null as number | null, [Validators.required]],
    roleId: [null as number | null, [Validators.required]],
  });

  readonly visibleRows = computed(() =>
    filterRows(this.rows(), this.filter(), (row) => [
      this.userLabel(row.userId),
      this.roleLabel(row.roleId),
    ])
  );

  constructor() {
    this.load();
    this.usersApi.list().subscribe({ next: (res) => this.users.set(res) });
    this.rolesApi.list().subscribe({ next: (res) => this.roles.set(res) });
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

  userLabel(id: number | undefined): string {
    return this.users().find((u) => u.id === id)?.username ?? `#${id}`;
  }

  roleLabel(id: number | undefined): string {
    return this.roles().find((r) => r.id === id)?.name ?? `#${id}`;
  }

  openCreate(): void {
    this.form.reset({ userId: null, roleId: null });
    this.dialogVisible.set(true);
  }

  submit(): void {
    const val = this.form.getRawValue();
    if (!val.userId || !val.roleId) {
      this.form.markAllAsTouched();
      return;
    }
    const payload: RoleUserPayload = {
      userId: val.userId,
      roleId: val.roleId,
      status: 'active',
    };
    this.saving.set(true);
    this.api.create(payload).subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success('Asignación vinculada');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo vincular', toApiMessage(err));
      },
    });
  }

  remove(row: RoleUser): void {
    this.confirmation.confirm({
      header: 'Retirar asignación',
      message: `¿Retirar el rol «${this.roleLabel(row.roleId)}» al usuario «${this.userLabel(row.userId)}»?`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Retirar',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.remove(row.id).subscribe({
          next: () => {
            this.notify.warn('Asignación retirada');
            this.load();
          },
          error: (err: unknown) => this.notify.error('No se pudo retirar', toApiMessage(err)),
        }),
    });
  }
}
