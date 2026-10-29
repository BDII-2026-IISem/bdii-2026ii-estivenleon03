import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../../environments/environment';
import { Sale, SaleCreatePayload } from '../models/sale.model';
import { SaleApi } from './sale-api';

const MOCK_SALE: Sale = {
  id: 1,
  client: 10,
  clientName: 'Carlos Pérez',
  saleDate: '2026-10-28T10:00:00-05:00',
  subtotal: '100.00',
  tax: '19.00',
  discounts: '0.00',
  total: '119.00',
  status: 'active',
  items: [
    {
      productId: 5,
      productName: 'Vacuna Antirrábica',
      quantity: 1,
      unitPrice: '100.00',
      lineTotal: '100.00',
    },
  ],
};

describe('SaleApi', () => {
  let api: SaleApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(SaleApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('debe enviar POST /api/payments/ con clientId e items', () => {
    const payload: SaleCreatePayload = {
      clientId: 10,
      saleDate: '2026-10-28T10:00:00-05:00',
      discounts: '0.00',
      items: [{ productId: 5, quantity: 1 }],
    };

    let result: Sale | undefined;
    api.create(payload).subscribe((res) => (result = res));

    const req = http.expectOne('http://localhost:8000/api/payments/');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(payload);
    req.flush(MOCK_SALE);

    expect(result).toEqual(MOCK_SALE);
  });
});
