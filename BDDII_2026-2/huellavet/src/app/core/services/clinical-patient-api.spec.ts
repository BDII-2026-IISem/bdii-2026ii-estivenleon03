import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../../environments/environment';
import { ConsultaService } from './consulta.service';
import { MascotaService } from './mascota.service';

describe('Patient and consultation APIs', () => {
  let pets: MascotaService;
  let consultations: ConsultaService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    pets = TestBed.inject(MascotaService);
    consultations = TestBed.inject(ConsultaService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('uses the persistent pets endpoint and sends the selected owner ID', () => {
    const payload = {
      owner: 8,
      name: 'Luna',
      species: 'Canino',
      breed: 'Labrador',
      birth_date: null,
      gender: null,
      description: '',
      is_active: true,
    };

    pets.createMascota(payload).subscribe();
    const request = http.expectOne(`${environment.apiUrl}/pets/`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body.owner).toBe(8);
    request.flush({ id: 3, ...payload });
  });

  it('uses the consultations endpoint and sends pet and veterinarian IDs', () => {
    const payload = {
      pet: 3,
      veterinarian: 5,
      appointment: null,
      title: 'Control',
      description: '',
      temperature_c: null,
      weight_kg: null,
      heart_rate: null,
      symptoms: 'Sin síntomas',
      diagnosis: 'Buen estado',
      is_active: true,
    };

    consultations.createConsulta(payload).subscribe();
    const request = http.expectOne(`${environment.apiUrl}/consultations/`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(payload);
    request.flush({ id: 9, ...payload });
  });
});
