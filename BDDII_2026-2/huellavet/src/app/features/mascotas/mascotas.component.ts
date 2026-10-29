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
import { Mascota, MascotaPayload } from '../../core/models/mascota.model';
import { Propietario } from '../../core/models/propietario.model';
import { MascotaService } from '../../core/services/mascota.service';
import { NotificationService } from '../../core/services/notification.service';
import { PropietarioApi } from '../../core/services/propietario-api';
import { toApiMessage } from '../../core/utils/to-api-message';

@Component({
  selector: 'app-mascotas',
  standalone: true,
  imports: [
    ButtonModule,
    DatePipe,
    DialogModule,
    FormsModule,
    MessageModule,
    TableModule,
    TagModule,
  ],
  templateUrl: './mascotas.component.html',
  styleUrl: './mascotas.component.css',
  host: { class: 'block' },
})
export class MascotasComponent {
  private readonly api = inject(MascotaService);
  private readonly ownersApi = inject(PropietarioApi);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);

  readonly pets = signal<Mascota[]>([]);
  readonly owners = signal<Propietario[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly dialogVisible = signal(false);
  readonly saving = signal(false);
  readonly editing = signal<Mascota | null>(null);
  readonly activeOwners = computed(() => {
    const currentOwnerId = this.editing()?.owner;
    return this.owners().filter(
      (owner) => owner.status === 'active' || owner.id === currentOwnerId
    );
  });
  currentPet: MascotaPayload = this.emptyPet();

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({ pets: this.api.getMascotas(), owners: this.ownersApi.list() }).subscribe({
      next: ({ pets, owners }) => {
        this.pets.set(pets);
        this.owners.set(owners);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }

  ownerName(ownerId: number): string {
    return this.owners().find((owner) => owner.id === ownerId)?.nombre ?? `Propietario #${ownerId}`;
  }

  openCreate(): void {
    this.editing.set(null);
    this.currentPet = this.emptyPet();
    this.dialogVisible.set(true);
  }

  openEdit(pet: Mascota): void {
    this.editing.set(pet);
    this.currentPet = {
      owner: pet.owner,
      name: pet.name,
      species: pet.species,
      breed: pet.breed,
      birth_date: pet.birth_date,
      gender: pet.gender,
      description: pet.description,
      is_active: pet.is_active,
    };
    this.dialogVisible.set(true);
  }

  save(): void {
    if (!this.currentPet.name.trim() || !this.currentPet.owner) return;
    const current = this.editing();
    this.saving.set(true);
    const request = current
      ? this.api.updateMascota(current.id, this.currentPet)
      : this.api.createMascota(this.currentPet);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success(current ? 'Mascota actualizada' : 'Mascota registrada');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar la mascota', toApiMessage(err));
      },
    });
  }

  remove(pet: Mascota): void {
    this.confirmation.confirm({
      header: 'Eliminar mascota',
      message: `¿Eliminar a ${pet.name}? La operación puede rechazarse si conserva citas o consultas asociadas.`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Eliminar',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.deleteMascota(pet.id).subscribe({
          next: () => {
            this.notify.warn('Mascota eliminada');
            this.load();
          },
          error: (err: unknown) =>
            this.notify.error('No se pudo eliminar la mascota', toApiMessage(err)),
        }),
    });
  }

  private emptyPet(): MascotaPayload {
    return {
      owner: 0,
      name: '',
      species: '',
      breed: '',
      birth_date: null,
      gender: null,
      description: '',
      is_active: true,
    };
  }
}
