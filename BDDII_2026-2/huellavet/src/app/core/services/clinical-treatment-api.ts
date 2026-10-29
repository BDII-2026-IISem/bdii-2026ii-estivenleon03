import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Prescription,
  PrescriptionPayload,
  Vaccine,
  VaccineApplication,
  VaccineApplicationPayload,
  VaccineBatch,
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

  vaccineBatches(): Observable<VaccineBatch[]> {
    return this.http.get<VaccineBatch[]>(`${this.base}/vaccine-batches/`);
  }

  vaccineApplications(): Observable<VaccineApplication[]> {
    return this.http.get<VaccineApplication[]>(`${this.base}/vaccine-applications/`);
  }

  createVaccineApplication(payload: VaccineApplicationPayload): Observable<VaccineApplication> {
    return this.http.post<VaccineApplication>(`${this.base}/vaccine-applications/`, payload);
  }
}
