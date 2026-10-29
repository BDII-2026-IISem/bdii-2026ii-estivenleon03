import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../../environments/environment';
import { Propietario } from '../models/propietario.model';
import { PropietarioApi } from './propietario-api';

const MOCK_PROPIETARIO: Propietario = {
  id: 1,
  nombre: 'Carlos Pérez',
  documento: '1098765432',
  telefono: '3001234567',
  email: 'carlos@example.com',
  direccion: 'Calle 10 # 20-30',
  status: 'active',
};

describe('PropietarioApi', () => {
  let api: PropietarioApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(PropietarioApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('debe llamar a /api/owners/ con barra final', () => {
    expect(environment.apiUrl.endsWith('/api')).toBe(true);

    let result: Propietario[] | undefined;
    api.list().subscribe((data) => (result = data));

    const req = http.expectOne('http://localhost:8000/api/owners/');
    expect(req.request.method).toBe('GET');
    req.flush([MOCK_PROPIETARIO]);

    expect(result).toEqual([MOCK_PROPIETARIO]);
  });

  it('debe enviar la baja lógica mediante DELETE respondiendo 204', () => {
    api.remove(1).subscribe();
    const req = http.expectOne('http://localhost:8000/api/owners/1/');
    expect(req.request.method).toBe('DELETE');
    req.flush(null, { status: 204, statusText: 'No Content' });
  });
});
