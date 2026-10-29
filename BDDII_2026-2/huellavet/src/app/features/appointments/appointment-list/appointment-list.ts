import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ConfirmationService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { forkJoin } from 'rxjs';
import { Appointment, AppointmentPayload, AppointmentStatus } from '../../../core/models/appointment.model';
import { Mascota } from '../../../core/models/mascota.model';
import { Propietario } from '../../../core/models/propietario.model';
import { Veterinarian } from '../../../core/models/veterinarian.model';
import { AppointmentApi } from '../../../core/services/appointment-api';
import { MascotaService } from '../../../core/services/mascota.service';
import { NotificationService } from '../../../core/services/notification.service';
import { PropietarioApi } from '../../../core/services/propietario-api';
import { VeterinarianApi } from '../../../core/services/veterinarian-api';
import { toApiMessage } from '../../../core/utils/to-api-message';

interface AppointmentForm {
  pet: number;
  veterinarian: number;
  start_time: string;
  end_time: string;
  reason: string;
  status: AppointmentStatus;
  is_active: boolean;
}

@Component({
  selector: 'app-appointment-list',
  standalone: true,
  imports: [ButtonModule, DatePipe, DialogModule, FormsModule, MessageModule, TableModule, TagModule],
  templateUrl: './appointment-list.html',
  host: { class: 'block' },
})
export class AppointmentList {
  private readonly api = inject(AppointmentApi);
  private readonly petsApi = inject(MascotaService);
  private readonly ownersApi = inject(PropietarioApi);
  private readonly veterinariansApi = inject(VeterinarianApi);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);

  readonly appointments = signal<Appointment[]>([]);
  readonly pets = signal<Mascota[]>([]);
  readonly owners = signal<Propietario[]>([]);
  readonly veterinarians = signal<Veterinarian[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly dialogVisible = signal(false);
  readonly editing = signal<Appointment | null>(null);
  readonly activePets = computed(() => {
    const currentPetId = this.editing()?.pet;
    return this.pets().filter((pet) => pet.is_active || pet.id === currentPetId);
  });
  readonly activeVeterinarians = computed(() => {
    const currentId = this.editing()?.veterinarian;
    return this.veterinarians().filter((vet) => vet.is_active || vet.id === currentId);
  });
  readonly statuses: Array<{ value: AppointmentStatus; label: string }> = [
    { value: 'SCHEDULED', label: 'Programada' },
    { value: 'CONFIRMED', label: 'Confirmada' },
    { value: 'IN_CONSULTATION', label: 'En consulta' },
    { value: 'COMPLETED', label: 'Completada' },
    { value: 'CANCELLED', label: 'Cancelada' },
  ];
  current: AppointmentForm = this.emptyForm();

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      appointments: this.api.list(),
      pets: this.petsApi.getMascotas(),
      owners: this.ownersApi.list(),
      veterinarians: this.veterinariansApi.list(),
    }).subscribe({
      next: (data) => {
        this.appointments.set(data.appointments);
        this.pets.set(data.pets);
        this.owners.set(data.owners);
        this.veterinarians.set(data.veterinarians);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }

  petName(petId: number): string {
    return this.pets().find((pet) => pet.id === petId)?.name ?? `Mascota #${petId}`;
  }

  ownerNameForPet(petId: number): string {
    const pet = this.pets().find((item) => item.id === petId);
    return this.owners().find((owner) => owner.id === pet?.owner)?.nombre ?? '—';
  }

  veterinarianName(veterinarianId: number): string {
    return this.veterinarians().find((vet) => vet.id === veterinarianId)?.name ??
      `Veterinario #${veterinarianId}`;
  }

  openCreate(): void {
    this.editing.set(null);
    this.current = this.emptyForm();
    this.dialogVisible.set(true);
  }

  openEdit(item: Appointment): void {
    this.editing.set(item);
    this.current = {
      pet: item.pet,
      veterinarian: item.veterinarian,
      start_time: this.toLocalDateTime(item.start_time),
      end_time: this.toLocalDateTime(item.end_time),
      reason: item.reason,
      status: item.status,
      is_active: item.is_active,
    };
    this.dialogVisible.set(true);
  }

  save(): void {
    const form = this.current;
    if (!form.pet || !form.veterinarian || !form.reason.trim() || !form.start_time || !form.end_time) return;
    const startsAt = new Date(form.start_time);
    const endsAt = new Date(form.end_time);
    if (endsAt <= startsAt) {
      this.notify.warn('Revisa el horario', 'La hora de fin debe ser posterior a la hora de inicio.');
      return;
    }

    const payload: AppointmentPayload = {
      ...form,
      start_time: startsAt.toISOString(),
      end_time: endsAt.toISOString(),
    };
    const existing = this.editing();
    this.saving.set(true);
    const request = existing
      ? this.api.update(existing.id, payload)
      : this.api.create(payload);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success(existing ? 'Cita actualizada' : 'Cita registrada');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar la cita', toApiMessage(err));
      },
    });
  }

  remove(item: Appointment): void {
    this.confirmation.confirm({
      header: 'Eliminar cita',
      message: `¿Eliminar la cita de ${this.petName(item.pet)}?`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Eliminar',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.remove(item.id).subscribe({
          next: () => {
            this.notify.warn('Cita eliminada');
            this.load();
          },
          error: (err: unknown) => this.notify.error('No se pudo eliminar la cita', toApiMessage(err)),
        }),
    });
  }

  statusLabel(status: AppointmentStatus): string {
    return this.statuses.find((option) => option.value === status)?.label ?? status;
  }

  statusSeverity(status: AppointmentStatus): 'success' | 'info' | 'warn' | 'danger' | 'secondary' {
    if (status === 'COMPLETED') return 'success';
    if (status === 'CONFIRMED') return 'info';
    if (status === 'CANCELLED') return 'danger';
    if (status === 'IN_CONSULTATION') return 'warn';
    return 'secondary';
  }

  private emptyForm(): AppointmentForm {
    const start = new Date();
    start.setMinutes(start.getMinutes() + 30);
    start.setSeconds(0, 0);
    const end = new Date(start.getTime() + 30 * 60 * 1000);
    return {
      pet: 0,
      veterinarian: 0,
      start_time: this.toLocalDateTime(start.toISOString()),
      end_time: this.toLocalDateTime(end.toISOString()),
      reason: '',
      status: 'SCHEDULED',
      is_active: true,
    };
  }

  private toLocalDateTime(value: string): string {
    const date = new Date(value);
    const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
    return localDate.toISOString().slice(0, 16);
  }
}
