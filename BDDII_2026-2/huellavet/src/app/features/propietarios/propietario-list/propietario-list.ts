import { Component, computed, inject, signal } from '@angular/core';
import { ConfirmationService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { Propietario, PropietarioPayload } from '../../../core/models/propietario.model';
import { NotificationService } from '../../../core/services/notification.service';
import { toApiMessage } from '../../../core/utils/to-api-message';
import { filterRows } from '../../../core/utils/filter-rows';
import { EmptyState } from '../../../shared/ui/empty-state/empty-state';
import { PageHeader } from '../../../shared/ui/page-header/page-header';
import { StatusTag } from '../../../shared/ui/status-tag/status-tag';
import { PropietarioApi } from '../../../core/services/propietario-api';
import { PropietarioForm } from '../propietario-form/propietario-form';

@Component({
  selector: 'app-propietario-list',
  standalone: true,
  imports: [
    ButtonModule,
    DialogModule,
    EmptyState,
    InputTextModule,
    MessageModule,
    PageHeader,
    StatusTag,
    TableModule,
    TagModule,
    TooltipModule,
    PropietarioForm,
  ],
  templateUrl: './propietario-list.html',
  styleUrl: './propietario-list.css',
  host: { class: 'block' },
})
export class PropietarioList {
  private readonly api = inject(PropietarioApi);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);

  readonly rows = signal<Propietario[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly filter = signal('');
  readonly dialogVisible = signal(false);
  readonly editing = signal<Propietario | null>(null);
  readonly resetKey = signal(0);

  readonly visibleRows = computed(() =>
    filterRows(this.rows(), this.filter(), (p) => [p.nombre, p.email, p.telefono, p.documento])
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
    this.resetKey.update((k) => k + 1);
    this.dialogVisible.set(true);
  }

  openEdit(propietario: Propietario): void {
    this.editing.set(propietario);
    this.resetKey.update((k) => k + 1);
    this.dialogVisible.set(true);
  }

  save(payload: PropietarioPayload): void {
    const current = this.editing();
    this.saving.set(true);
    const request = current
      ? this.api.update(current.id, payload)
      : this.api.create({ ...payload, status: 'active' });

    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success(current ? 'Propietario actualizado' : 'Propietario registrado');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar', toApiMessage(err));
      },
    });
  }

  remove(propietario: Propietario): void {
    this.confirmation.confirm({
      header: 'Dar de baja',
      message: `¿Dar de baja al propietario ${propietario.nombre}? Su historial médico se conservará.`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Dar de baja',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.remove(propietario.id).subscribe({
          next: () => {
            this.notify.warn('Propietario dado de baja');
            this.load();
          },
          error: (err: unknown) => this.notify.error('No se pudo dar de baja', toApiMessage(err)),
        }),
    });
  }
}
