import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../../environments/environment';
import { AppointmentApi } from './appointment-api';

describe('AppointmentApi', () => {
  let api: AppointmentApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(AppointmentApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('lists appointments from the configured API base', () => {
    api.list().subscribe();
    const request = http.expectOne(`${environment.apiUrl}/appointments/`);
    expect(request.request.method).toBe('GET');
    request.flush([]);
  });

  it('creates appointments using pet and veterinarian IDs', () => {
    const payload = {
      pet: 12,
      veterinarian: 4,
      start_time: '2026-10-29T14:00:00Z',
      end_time: '2026-10-29T14:30:00Z',
      reason: 'Control',
      status: 'SCHEDULED' as const,
      is_active: true,
    };

    api.create(payload).subscribe();
    const request = http.expectOne(`${environment.apiUrl}/appointments/`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(payload);
    request.flush({ id: 21, ...payload });
  });
});
