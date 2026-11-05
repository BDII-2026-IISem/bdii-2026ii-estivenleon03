import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Veterinarian, VeterinarianPayload } from '../models/veterinarian.model';

@Injectable({ providedIn: 'root' })
export class VeterinarianApi {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/veterinarians`;

  list(): Observable<Veterinarian[]> {
    return this.http.get<Veterinarian[]>(`${this.base}/`);
  }

  create(payload: VeterinarianPayload): Observable<Veterinarian> {
    return this.http.post<Veterinarian>(`${this.base}/`, payload);
  }

  update(id: number, payload: Partial<VeterinarianPayload>): Observable<Veterinarian> {
    return this.http.patch<Veterinarian>(`${this.base}/${id}/`, payload);
  }
}
