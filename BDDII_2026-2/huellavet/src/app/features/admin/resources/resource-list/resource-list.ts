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
import { TextareaModule } from 'primeng/textarea';
import { TooltipModule } from 'primeng/tooltip';
import { HttpMethod, STATUS_OPTIONS, Status } from '../../../../core/models/api.model';
import { Resource, ResourcePayload } from '../../../../core/models/resource.model';
import { NotificationService } from '../../../../core/services/notification.service';
import { toApiMessage } from '../../../../core/utils/to-api-message';
import { filterRows } from '../../../../core/utils/filter-rows';
import { HTTP_METHODS, methodSeverity } from '../../../../core/utils/http-method';
import { EmptyState } from '../../../../shared/ui/empty-state/empty-state';
import { PageHeader } from '../../../../shared/ui/page-header/page-header';
import { StatusTag } from '../../../../shared/ui/status-tag/status-tag';
import { HasPermission } from '../../../../shared/directives/has-permission';
import { ResourceApi } from '../resource-api';

@Component({
  selector: 'app-resource-list',
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
    TextareaModule,
    TooltipModule,
  ],
  templateUrl: './resource-list.html',
  styleUrl: './resource-list.css',
  host: { class: 'block' },
})
export class ResourceList {
  private readonly api = inject(ResourceApi);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);
  private readonly fb = inject(NonNullableFormBuilder);

  readonly statusOptions = STATUS_OPTIONS;
  readonly methods = HTTP_METHODS;
  readonly methodSeverity = methodSeverity;

  readonly rows = signal<Resource[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly filter = signal('');
  readonly dialogVisible = signal(false);
  readonly editing = signal<Resource | null>(null);

  readonly form = this.fb.group({
    method: ['GET' as HttpMethod, [Validators.required]],
    path: ['', [Validators.required, Validators.pattern(/^\/api\//)]],
    description: [''],
    status: ['active' as Status, [Validators.required]],
  });

  readonly visibleRows = computed(() =>
    filterRows(this.rows(), this.filter(), (row) => [row.method, row.path, row.description])
  );

  constructor() {
    this.load();
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

  openCreate(): void {
    this.editing.set(null);
    this.form.reset({ method: 'GET', path: '/api/', description: '', status: 'active' });
    this.dialogVisible.set(true);
  }

  openEdit(row: Resource): void {
    this.editing.set(row);
    this.form.reset({
      method: row.method,
      path: row.path,
      description: row.description ?? '',
      status: row.status,
    });
    this.dialogVisible.set(true);
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const val = this.form.getRawValue();
    const payload: ResourcePayload = {
      method: val.method,
      path: val.path.trim(),
      description: val.description.trim() || null,
      status: val.status,
    };
    const current = this.editing();
    this.saving.set(true);

    const req$ = current ? this.api.update(current.id, payload) : this.api.create(payload);
    req$.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success(current ? 'Recurso actualizado' : 'Recurso creado');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar', toApiMessage(err));
      },
    });
  }

  remove(row: Resource): void {
    this.confirmation.confirm({
      header: 'Dar de baja',
      message: `¿Desactivar el recurso «${row.method} ${row.path}»?`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Desactivar',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.remove(row.id).subscribe({
          next: () => {
            this.notify.warn('Recurso desactivado');
            this.load();
          },
          error: (err: unknown) => this.notify.error('No se pudo desactivar', toApiMessage(err)),
        }),
    });
  }
}
