import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../../environments/environment';
import { Sale, SalePaymentCreatePayload } from '../models/sale.model';
import { PaymentApi } from './payment-api';

describe('PaymentApi', () => {
  let api: PaymentApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(PaymentApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('registra un abono de venta en la operación de pagos del backend', () => {
    const payload: SalePaymentCreatePayload = { method: 'TRANSFER', amount: '25.00' };
    const sale: Sale = {
      id: 8,
      client: 2,
      saleDate: '2026-10-28T10:00:00-05:00',
      subtotal: '25.00',
      tax: '4.75',
      discounts: '0.00',
      total: '29.75',
      status: 'active',
    };
    let result: Sale | undefined;

    api.addSalePayment(8, payload).subscribe((response) => (result = response));

    const request = http.expectOne(`${environment.apiUrl}/sales/8/payments/`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(payload);
    request.flush(sale);
    expect(result).toEqual(sale);
  });

});
