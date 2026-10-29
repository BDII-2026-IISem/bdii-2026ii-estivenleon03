import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../../environments/environment';
import { ClinicalTreatmentApi } from './clinical-treatment-api';

describe('ClinicalTreatmentApi', () => {
  let api: ClinicalTreatmentApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(ClinicalTreatmentApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('loads prescription and vaccine history from the API', () => {
    api.prescriptions().subscribe();
    http.expectOne(`${environment.apiUrl}/prescriptions/`).flush([]);
    api.vaccineApplications().subscribe();
    http.expectOne(`${environment.apiUrl}/vaccine-applications/`).flush([]);
  });

  it('creates a vaccine application linked to an existing consultation and batch', () => {
    const payload = {
      consultation: 7,
      vaccine_batch: 3,
      name: 'Rabia',
      description: '',
      dosage_ml: 1,
      notes: '',
      is_active: true,
    };

    api.createVaccineApplication(payload).subscribe();
    const request = http.expectOne(`${environment.apiUrl}/vaccine-applications/`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(payload);
    request.flush({ id: 2, ...payload });
  });
});
