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
import { Consulta } from '../../core/models/consulta.model';
import {
  Prescription,
  PrescriptionPayload,
  Vaccine,
  VaccineBatchPayload,
  VaccineApplication,
  VaccineApplicationPayload,
  VaccineBatch,
  VaccinePayload,
} from '../../core/models/clinical-treatment.model';
import { Mascota } from '../../core/models/mascota.model';
import { ConsultaService } from '../../core/services/consulta.service';
import { ClinicalTreatmentApi } from '../../core/services/clinical-treatment-api';
import { MascotaService } from '../../core/services/mascota.service';
import { NotificationService } from '../../core/services/notification.service';
import { toApiMessage } from '../../core/utils/to-api-message';

@Component({
  selector: 'app-clinical-treatments',
  standalone: true,
  imports: [ButtonModule, DatePipe, DialogModule, FormsModule, MessageModule, TableModule, TagModule],
  templateUrl: './clinical-treatments.html',
  host: { class: 'block' },
})
export class ClinicalTreatments {
  private readonly api = inject(ClinicalTreatmentApi);
  private readonly consultationsApi = inject(ConsultaService);
  private readonly petsApi = inject(MascotaService);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);

  readonly prescriptions = signal<Prescription[]>([]);
  readonly vaccineApplications = signal<VaccineApplication[]>([]);
  readonly consultations = signal<Consulta[]>([]);
  readonly pets = signal<Mascota[]>([]);
  readonly vaccines = signal<Vaccine[]>([]);
  readonly batches = signal<VaccineBatch[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly prescriptionDialog = signal(false);
  readonly vaccineDialog = signal(false);
  readonly vaccineCatalogDialog = signal(false);
  readonly batchDialog = signal(false);
  readonly editingPrescription = signal<Prescription | null>(null);
  readonly editingVaccine = signal<Vaccine | null>(null);
  readonly editingBatch = signal<VaccineBatch | null>(null);
  readonly availableBatches = computed(() => {
    const today = new Date().toISOString().slice(0, 10);
    return this.batches().filter(
      (batch) =>
        batch.is_active &&
        this.vaccines().some((vaccine) => vaccine.id === batch.vaccine && vaccine.is_active) &&
        batch.stock_quantity > 0 &&
        batch.expiration_date >= today
    );
  });
  prescriptionForm: PrescriptionPayload = this.emptyPrescription();
  vaccineForm: VaccineApplicationPayload = this.emptyVaccineApplication();
  vaccineCatalogForm: VaccinePayload = this.emptyVaccine();
  batchForm: VaccineBatchPayload = this.emptyBatch();

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      prescriptions: this.api.prescriptions(),
      vaccineApplications: this.api.vaccineApplications(),
      consultations: this.consultationsApi.getConsultas(),
      pets: this.petsApi.getMascotas(),
      vaccines: this.api.vaccines(),
      batches: this.api.vaccineBatches(),
    }).subscribe({
      next: (data) => {
        this.prescriptions.set(data.prescriptions);
        this.vaccineApplications.set(data.vaccineApplications);
        this.consultations.set(data.consultations);
        this.pets.set(data.pets);
        this.vaccines.set(data.vaccines);
        this.batches.set(data.batches);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }

  consultationLabel(id: number): string {
    const consultation = this.consultations().find((item) => item.id === id);
    if (!consultation) return `Consulta #${id}`;
    return `#${id} · ${this.petName(consultation.pet)} · ${consultation.title}`;
  }

  petNameForConsultation(id: number): string {
    const consultation = this.consultations().find((item) => item.id === id);
    return consultation ? this.petName(consultation.pet) : 'Mascota no disponible';
  }

  petName(petId: number): string {
    return this.pets().find((pet) => pet.id === petId)?.name ?? `Mascota #${petId}`;
  }

  vaccineName(vaccineId: number): string {
    return this.vaccines().find((vaccine) => vaccine.id === vaccineId)?.name ?? `Vacuna #${vaccineId}`;
  }

  batchLabel(id: number): string {
    const batch = this.batches().find((item) => item.id === id);
    return batch
      ? `${this.vaccineName(batch.vaccine)} · lote ${batch.batch_number}`
      : `Lote #${id}`;
  }

  openNewPrescription(): void {
    this.editingPrescription.set(null);
    this.prescriptionForm = this.emptyPrescription();
    this.prescriptionDialog.set(true);
  }

  editPrescription(item: Prescription): void {
    this.editingPrescription.set(item);
    this.prescriptionForm = {
      consultation: item.consultation,
      medication_name: item.medication_name,
      description: item.description,
      dosage: item.dosage,
      frequency: item.frequency,
      duration_days: item.duration_days,
      is_active: item.is_active,
    };
    this.prescriptionDialog.set(true);
  }

  savePrescription(): void {
    const form = this.prescriptionForm;
    if (!form.consultation || !form.medication_name.trim() || !form.dosage.trim() ||
      !form.frequency.trim() || form.duration_days < 1) return;

    const current = this.editingPrescription();
    this.saving.set(true);
    const request = current
      ? this.api.updatePrescription(current.id, form)
      : this.api.createPrescription(form);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.prescriptionDialog.set(false);
        this.notify.success(current ? 'Prescripción actualizada' : 'Prescripción registrada');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar la prescripción', toApiMessage(err));
      },
    });
  }

  removePrescription(item: Prescription): void {
    this.confirmation.confirm({
      header: 'Eliminar prescripción',
      message: `¿Eliminar la prescripción de ${item.medication_name}?`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Eliminar',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.deletePrescription(item.id).subscribe({
          next: () => {
            this.notify.warn('Prescripción eliminada');
            this.load();
          },
          error: (err: unknown) =>
            this.notify.error('No se pudo eliminar la prescripción', toApiMessage(err)),
        }),
    });
  }

  openVaccineApplication(): void {
    this.vaccineForm = this.emptyVaccineApplication();
    this.vaccineDialog.set(true);
  }

  selectVaccineBatch(batchId: number): void {
    this.vaccineForm.vaccine_batch = batchId;
    const batch = this.batches().find((item) => item.id === batchId);
    const vaccine = this.vaccines().find((item) => item.id === batch?.vaccine);
    if (vaccine) this.vaccineForm.name = vaccine.name;
  }

  saveVaccineApplication(): void {
    const form = this.vaccineForm;
    if (!form.consultation || !form.vaccine_batch || !form.name.trim()) return;
    this.saving.set(true);
    this.api.createVaccineApplication(form).subscribe({
      next: () => {
        this.saving.set(false);
        this.vaccineDialog.set(false);
        this.notify.success('Aplicación de vacuna registrada', 'El inventario del lote se actualizó.');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo registrar la aplicación', toApiMessage(err));
      },
    });
  }

  openNewVaccine(): void {
    this.editingVaccine.set(null);
    this.vaccineCatalogForm = this.emptyVaccine();
    this.vaccineCatalogDialog.set(true);
  }

  editVaccine(item: Vaccine): void {
    this.editingVaccine.set(item);
    this.vaccineCatalogForm = {
      name: item.name,
      description: item.description,
      is_active: item.is_active,
    };
    this.vaccineCatalogDialog.set(true);
  }

  saveVaccine(): void {
    if (!this.vaccineCatalogForm.name.trim()) return;
    const current = this.editingVaccine();
    const payload = {
      ...this.vaccineCatalogForm,
      name: this.vaccineCatalogForm.name.trim(),
    };
    this.saving.set(true);
    const request = current
      ? this.api.updateVaccine(current.id, payload)
      : this.api.createVaccine(payload);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.vaccineCatalogDialog.set(false);
        this.notify.success(current ? 'Vacuna actualizada' : 'Vacuna registrada');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar la vacuna', toApiMessage(err));
      },
    });
  }

  openNewBatch(): void {
    this.editingBatch.set(null);
    this.batchForm = this.emptyBatch();
    this.batchDialog.set(true);
  }

  editBatch(item: VaccineBatch): void {
    this.editingBatch.set(item);
    this.batchForm = {
      vaccine: item.vaccine,
      name: item.name,
      batch_number: item.batch_number,
      description: item.description,
      expiration_date: item.expiration_date,
      stock_quantity: item.stock_quantity,
      is_active: item.is_active,
    };
    this.batchDialog.set(true);
  }

  saveBatch(): void {
    const form = this.batchForm;
    if (!form.vaccine || !form.name.trim() || !form.batch_number.trim() || !form.expiration_date) return;
    const current = this.editingBatch();
    const payload = {
      ...form,
      name: form.name.trim(),
      batch_number: form.batch_number.trim(),
    };
    this.saving.set(true);
    const request = current
      ? this.api.updateVaccineBatch(current.id, payload)
      : this.api.createVaccineBatch(payload);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.batchDialog.set(false);
        this.notify.success(current ? 'Lote actualizado' : 'Lote registrado');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar el lote', toApiMessage(err));
      },
    });
  }

  private emptyPrescription(): PrescriptionPayload {
    return {
      consultation: 0,
      medication_name: '',
      description: '',
      dosage: '',
      frequency: '',
      duration_days: 1,
      is_active: true,
    };
  }

  private emptyVaccineApplication(): VaccineApplicationPayload {
    return {
      consultation: 0,
      vaccine_batch: 0,
      name: '',
      description: '',
      dosage_ml: 1,
      notes: '',
      is_active: true,
    };
  }

  private emptyVaccine(): VaccinePayload {
    return { name: '', description: '', is_active: true };
  }

  private emptyBatch(): VaccineBatchPayload {
    return {
      vaccine: 0,
      name: '',
      batch_number: '',
      description: '',
      expiration_date: '',
      stock_quantity: 0,
      is_active: true,
    };
  }
}
