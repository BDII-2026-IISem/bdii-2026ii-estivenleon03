import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../../environments/environment';
import { AppointmentPayment, AppointmentPaymentPayload, PaymentAudit } from '../models/payment.model';
import { AppointmentPaymentApi } from './appointment-payment-api';

describe('AppointmentPaymentApi', () => {
  let api: AppointmentPaymentApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(AppointmentPaymentApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('consulta y registra pagos de citas en el endpoint de payments', () => {
    const payload: AppointmentPaymentPayload = {
      appointment: 7,
      reference_type: 'APPOINTMENT',
      reference_id: 7,
      method: 'CASH',
      amount: '45.00',
      status: 'PAID',
    };
    const payment: AppointmentPayment = {
      id: 11,
      ...payload,
      payment_date: '2026-10-28T15:00:00Z',
    };

    api.list().subscribe((rows) => expect(rows).toEqual([payment]));
    const list = http.expectOne(`${environment.apiUrl}/payments/`);
    expect(list.request.method).toBe('GET');
    list.flush([payment]);

    api.create(payload).subscribe((row) => expect(row).toEqual(payment));
    const create = http.expectOne(`${environment.apiUrl}/payments/`);
    expect(create.request.method).toBe('POST');
    expect(create.request.body).toEqual(payload);
    create.flush(payment);
  });

  it('actualiza y elimina pagos de citas por su endpoint de detalle', () => {
    api.update(11, { status: 'CANCELLED' }).subscribe();
    const update = http.expectOne(`${environment.apiUrl}/payments/11/`);
    expect(update.request.method).toBe('PATCH');
    update.flush({ id: 11, status: 'CANCELLED' });

    api.remove(11).subscribe();
    const remove = http.expectOne(`${environment.apiUrl}/payments/11/`);
    expect(remove.request.method).toBe('DELETE');
    remove.flush(null);
  });

  it('consulta auditoría solo por GET y en una ruta independiente', () => {
    const audit: PaymentAudit = {
      id: 2,
      payment_id: 11,
      actionSale: 'DELETE',
      changed_at: '2026-10-28T15:05:00Z',
      changed_by: 'admin',
      before_data: { amount: '45.00' },
      after_data: null,
    };
    api.listAudits().subscribe((rows) => expect(rows).toEqual([audit]));
    const request = http.expectOne(`${environment.apiUrl}/payment-audits/`);
    expect(request.request.method).toBe('GET');
    request.flush([audit]);
  });
});
