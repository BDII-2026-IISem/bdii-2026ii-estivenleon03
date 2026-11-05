import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { forkJoin } from 'rxjs';
import { User } from '../../core/models/user.model';
import { Veterinarian, VeterinarianPayload } from '../../core/models/veterinarian.model';
import { NotificationService } from '../../core/services/notification.service';
import { UserApi } from '../admin/users/user-api';
import { VeterinarianApi } from '../../core/services/veterinarian-api';
import { toApiMessage } from '../../core/utils/to-api-message';

@Component({
  selector: 'app-veterinarian-list',
  standalone: true,
  imports: [ButtonModule, DialogModule, FormsModule, MessageModule, TableModule, TagModule],
  templateUrl: './veterinarian-list.html',
  host: { class: 'block' },
})
export class VeterinarianList {
  private readonly api = inject(VeterinarianApi);
  private readonly usersApi = inject(UserApi);
  private readonly notify = inject(NotificationService);

  readonly veterinarians = signal<Veterinarian[]>([]);
  readonly users = signal<User[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly dialogVisible = signal(false);
  readonly editing = signal<Veterinarian | null>(null);
  current: VeterinarianPayload = this.emptyForm();

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({ veterinarians: this.api.list(), users: this.usersApi.list() }).subscribe({
      next: ({ veterinarians, users }) => {
        this.veterinarians.set(veterinarians);
        this.users.set(users);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.editing.set(null);
    this.current = this.emptyForm();
    this.dialogVisible.set(true);
  }

  openEdit(item: Veterinarian): void {
    this.editing.set(item);
    this.current = {
      name: item.name,
      license_number: item.license_number,
      description: item.description,
      is_active: item.is_active,
      auth_user: item.auth_user,
    };
    this.dialogVisible.set(true);
  }

  save(): void {
    if (!this.current.name.trim()) return;
    const existing = this.editing();
    const payload = { ...this.current, name: this.current.name.trim() };
    this.saving.set(true);
    const request = existing
      ? this.api.update(existing.id, payload)
      : this.api.create(payload);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success(existing ? 'Veterinario actualizado' : 'Veterinario registrado');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar el veterinario', toApiMessage(err));
      },
    });
  }

  deactivate(item: Veterinarian): void {
    this.api.update(item.id, { is_active: false }).subscribe({
      next: () => {
        this.notify.warn('Veterinario dado de baja');
        this.load();
      },
      error: (err: unknown) =>
        this.notify.error('No se pudo dar de baja al veterinario', toApiMessage(err)),
    });
  }

  isAssignedToAnotherVeterinarian(userId: number): boolean {
    return this.veterinarians().some(
      (veterinarian) =>
        veterinarian.auth_user === userId && veterinarian.id !== this.editing()?.id
    );
  }

  private emptyForm(): VeterinarianPayload {
    return {
      name: '',
      license_number: null,
      description: '',
      is_active: true,
      auth_user: null,
    };
  }
}
