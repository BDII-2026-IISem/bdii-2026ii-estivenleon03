import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../../environments/environment';
import { Product } from '../models/product.model';
import { ProductApi } from './product-api';

const MOCK_PRODUCT: Product = {
  id: 1,
  productTypeId: 2,
  productTypeName: 'Medicamentos',
  name: 'Amoxicilina 250mg',
  brand: 'Zoetis',
  description: 'Antibiótico',
  price: '15.50',
  minStock: 5,
  quantity: 20,
  status: 'active',
};

describe('ProductApi', () => {
  let api: ProductApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(ProductApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('debe consultar el catálogo real de productos', () => {
    let result: Product[] | undefined;
    api.list().subscribe((data) => (result = data));

    const req = http.expectOne('http://localhost:8000/api/v1/products/');
    expect(req.request.method).toBe('GET');
    req.flush([MOCK_PRODUCT]);

    expect(result).toEqual([MOCK_PRODUCT]);
  });

  it('debe consultar productos con stock disponible en el endpoint de productos', () => {
    let result: Product[] | undefined;
    api.available().subscribe((data) => (result = data));

    const req = http.expectOne('http://localhost:8000/api/v1/products/available/');
    expect(req.request.method).toBe('GET');
    req.flush([MOCK_PRODUCT]);

    expect(result).toEqual([MOCK_PRODUCT]);
  });

  it('debe enviar la baja lógica de producto mediante DELETE respondiendo 204', () => {
    api.remove(1).subscribe();
    const req = http.expectOne('http://localhost:8000/api/v1/products/1/');
    expect(req.request.method).toBe('DELETE');
    req.flush(null, { status: 204, statusText: 'No Content' });
  });
});
