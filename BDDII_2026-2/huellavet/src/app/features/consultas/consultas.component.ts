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
import { Consulta, ConsultaPayload } from '../../core/models/consulta.model';
import { Mascota } from '../../core/models/mascota.model';
import { Propietario } from '../../core/models/propietario.model';
import { Veterinarian } from '../../core/models/veterinarian.model';
import { ConsultaService } from '../../core/services/consulta.service';
import { MascotaService } from '../../core/services/mascota.service';
import { NotificationService } from '../../core/services/notification.service';
import { PropietarioApi } from '../../core/services/propietario-api';
import { VeterinarianApi } from '../../core/services/veterinarian-api';
import { toApiMessage } from '../../core/utils/to-api-message';

@Component({
  selector: 'app-consultas',
  standalone: true,
  imports: [ButtonModule, DatePipe, DialogModule, FormsModule, MessageModule, TableModule, TagModule],
  templateUrl: './consultas.component.html',
  styleUrl: './consultas.component.css',
  host: { class: 'block' },
})
export class ConsultasComponent {
  private readonly api = inject(ConsultaService);
  private readonly petsApi = inject(MascotaService);
  private readonly ownersApi = inject(PropietarioApi);
  private readonly veterinariansApi = inject(VeterinarianApi);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);

  readonly consultations = signal<Consulta[]>([]);
  readonly pets = signal<Mascota[]>([]);
  readonly owners = signal<Propietario[]>([]);
  readonly veterinarians = signal<Veterinarian[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly dialogVisible = signal(false);
  readonly detailsVisible = signal(false);
  readonly editing = signal<Consulta | null>(null);
  readonly availablePets = computed(() => {
    const currentPetId = this.editing()?.pet;
    return this.pets().filter((pet) => pet.is_active || pet.id === currentPetId);
  });
  readonly availableVeterinarians = computed(() => {
    const currentId = this.editing()?.veterinarian;
    return this.veterinarians().filter((vet) => vet.is_active || vet.id === currentId);
  });
  currentConsultation: ConsultaPayload = this.emptyConsultation();
  selectedDetails: Consulta | null = null;

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      consultations: this.api.getConsultas(),
      pets: this.petsApi.getMascotas(),
      owners: this.ownersApi.list(),
      veterinarians: this.veterinariansApi.list(),
    }).subscribe({
      next: (data) => {
        this.consultations.set(data.consultations);
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
    this.currentConsultation = this.emptyConsultation();
    this.dialogVisible.set(true);
  }

  openEdit(item: Consulta): void {
    this.editing.set(item);
    this.currentConsultation = {
      pet: item.pet,
      veterinarian: item.veterinarian,
      appointment: item.appointment,
      title: item.title,
      description: item.description,
      temperature_c: item.temperature_c,
      weight_kg: item.weight_kg,
      heart_rate: item.heart_rate,
      symptoms: item.symptoms,
      diagnosis: item.diagnosis,
      is_active: item.is_active,
    };
    this.dialogVisible.set(true);
  }

  viewDetails(item: Consulta): void {
    this.selectedDetails = item;
    this.detailsVisible.set(true);
  }

  save(): void {
    const form = this.currentConsultation;
    if (!form.pet || !form.veterinarian || !form.title.trim() || !form.symptoms.trim() || !form.diagnosis.trim()) return;

    const current = this.editing();
    this.saving.set(true);
    const request = current
      ? this.api.updateConsulta(current.id, form)
      : this.api.createConsulta(form);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success(current ? 'Consulta actualizada' : 'Consulta registrada');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar la consulta', toApiMessage(err));
      },
    });
  }

  remove(item: Consulta): void {
    this.confirmation.confirm({
      header: 'Eliminar consulta',
      message: `¿Eliminar la consulta «${item.title}» de ${this.petName(item.pet)}?`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Eliminar',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.deleteConsulta(item.id).subscribe({
          next: () => {
            this.notify.warn('Consulta eliminada');
            this.load();
          },
          error: (err: unknown) =>
            this.notify.error('No se pudo eliminar la consulta', toApiMessage(err)),
        }),
    });
  }

  private emptyConsultation(): ConsultaPayload {
    return {
      pet: 0,
      veterinarian: 0,
      appointment: null,
      title: '',
      description: '',
      temperature_c: null,
      weight_kg: null,
      heart_rate: null,
      symptoms: '',
      diagnosis: '',
      is_active: true,
    };
  }
}
