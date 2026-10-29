import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Status } from '../models/api.model';
import { Propietario, PropietarioPayload } from '../models/propietario.model';

@Injectable({ providedIn: 'root' })
export class PropietarioApi {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/owners`;

  list(): Observable<Propietario[]> {
    return this.http.get<Propietario[]>(`${this.base}/`);
  }

  get(id: number): Observable<Propietario> {
    return this.http.get<Propietario>(`${this.base}/${id}/`);
  }

  create(payload: PropietarioPayload & { status: Status }): Observable<Propietario> {
    return this.http.post<Propietario>(`${this.base}/`, payload);
  }

  update(id: number, payload: Partial<PropietarioPayload>): Observable<Propietario> {
    return this.http.patch<Propietario>(`${this.base}/${id}/`, payload);
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/`);
  }
}
