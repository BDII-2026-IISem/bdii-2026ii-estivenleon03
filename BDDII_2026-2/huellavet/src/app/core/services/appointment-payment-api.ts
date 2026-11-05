import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AppointmentPayment, AppointmentPaymentPayload, PaymentAudit } from '../models/payment.model';

@Injectable({ providedIn: 'root' })
export class AppointmentPaymentApi {
  private readonly http = inject(HttpClient);
  private readonly paymentsBase = `${environment.apiUrl}/payments`;
  private readonly auditsBase = `${environment.apiUrl}/payment-audits`;

  list(): Observable<AppointmentPayment[]> {
    return this.http.get<AppointmentPayment[]>(`${this.paymentsBase}/`);
  }

  create(payload: AppointmentPaymentPayload): Observable<AppointmentPayment> {
    return this.http.post<AppointmentPayment>(`${this.paymentsBase}/`, payload);
  }

  update(id: number, payload: Partial<AppointmentPaymentPayload>): Observable<AppointmentPayment> {
    return this.http.patch<AppointmentPayment>(`${this.paymentsBase}/${id}/`, payload);
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.paymentsBase}/${id}/`);
  }

  listAudits(): Observable<PaymentAudit[]> {
    return this.http.get<PaymentAudit[]>(`${this.auditsBase}/`);
  }
}
