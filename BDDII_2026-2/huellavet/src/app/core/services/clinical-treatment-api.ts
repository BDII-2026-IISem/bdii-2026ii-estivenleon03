import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Prescription,
  PrescriptionPayload,
  Vaccine,
  VaccineBatchPayload,
  VaccineApplication,
  VaccineApplicationPayload,
  VaccineBatch,
  VaccinePayload,
} from '../models/clinical-treatment.model';

@Injectable({ providedIn: 'root' })
export class ClinicalTreatmentApi {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  prescriptions(): Observable<Prescription[]> {
    return this.http.get<Prescription[]>(`${this.base}/prescriptions/`);
  }

  createPrescription(payload: PrescriptionPayload): Observable<Prescription> {
    return this.http.post<Prescription>(`${this.base}/prescriptions/`, payload);
  }

  updatePrescription(id: number, payload: Partial<PrescriptionPayload>): Observable<Prescription> {
    return this.http.patch<Prescription>(`${this.base}/prescriptions/${id}/`, payload);
  }

  deletePrescription(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/prescriptions/${id}/`);
  }

  vaccines(): Observable<Vaccine[]> {
    return this.http.get<Vaccine[]>(`${this.base}/vaccines/`);
  }

  createVaccine(payload: VaccinePayload): Observable<Vaccine> {
    return this.http.post<Vaccine>(`${this.base}/vaccines/`, payload);
  }

  updateVaccine(id: number, payload: Partial<VaccinePayload>): Observable<Vaccine> {
    return this.http.patch<Vaccine>(`${this.base}/vaccines/${id}/`, payload);
  }

  vaccineBatches(): Observable<VaccineBatch[]> {
    return this.http.get<VaccineBatch[]>(`${this.base}/vaccine-batches/`);
  }

  createVaccineBatch(payload: VaccineBatchPayload): Observable<VaccineBatch> {
    return this.http.post<VaccineBatch>(`${this.base}/vaccine-batches/`, payload);
  }

  updateVaccineBatch(
    id: number,
    payload: Partial<VaccineBatchPayload>,
  ): Observable<VaccineBatch> {
    return this.http.patch<VaccineBatch>(`${this.base}/vaccine-batches/${id}/`, payload);
  }

  vaccineApplications(): Observable<VaccineApplication[]> {
    return this.http.get<VaccineApplication[]>(`${this.base}/vaccine-applications/`);
  }

  createVaccineApplication(payload: VaccineApplicationPayload): Observable<VaccineApplication> {
    return this.http.post<VaccineApplication>(`${this.base}/vaccine-applications/`, payload);
  }
}
