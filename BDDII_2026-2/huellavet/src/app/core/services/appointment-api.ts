import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Appointment, AppointmentPayload } from '../models/appointment.model';

@Injectable({ providedIn: 'root' })
export class AppointmentApi {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/appointments`;

  list(): Observable<Appointment[]> {
    return this.http.get<Appointment[]>(`${this.base}/`);
  }

  create(payload: AppointmentPayload): Observable<Appointment> {
    return this.http.post<Appointment>(`${this.base}/`, payload);
  }

  update(id: number, payload: Partial<AppointmentPayload>): Observable<Appointment> {
    return this.http.patch<Appointment>(`${this.base}/${id}/`, payload);
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/`);
  }
}
