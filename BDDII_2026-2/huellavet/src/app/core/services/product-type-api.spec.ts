import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../../environments/environment';
import { ProductType } from '../models/product-type.model';
import { ProductTypeApi } from './product-type-api';

const MOCK_TYPE: ProductType = {
  id: 1,
  name: 'Vacunas',
  description: 'Inmunizaciones para mascotas',
  status: 'active',
};

describe('ProductTypeApi', () => {
  let api: ProductTypeApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(ProductTypeApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('debe llamar a /api/vaccines/?status=active con barra final', () => {
    expect(environment.apiUrl.endsWith('/api')).toBe(true);

    let result: ProductType[] | undefined;
    api.list('active').subscribe((data) => (result = data));

    const req = http.expectOne('http://localhost:8000/api/vaccines/?status=active');
    expect(req.request.method).toBe('GET');
    req.flush([MOCK_TYPE]);

    expect(result).toEqual([MOCK_TYPE]);
  });

  it('debe enviar la baja lógica mediante DELETE respondiendo 204', () => {
    api.remove(1).subscribe();
    const req = http.expectOne('http://localhost:8000/api/vaccines/1/');
    expect(req.request.method).toBe('DELETE');
    req.flush(null, { status: 204, statusText: 'No Content' });
  });
});
