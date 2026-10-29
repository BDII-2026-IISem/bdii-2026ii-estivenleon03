import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Mascota, MascotaPayload } from '../models/mascota.model';

@Injectable({
  providedIn: 'root'
})
export class MascotaService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/pets`;

  getMascotas(): Observable<Mascota[]> {
    return this.http.get<Mascota[]>(`${this.apiUrl}/`);
  }

  getMascotaById(id: number): Observable<Mascota> {
    return this.http.get<Mascota>(`${this.apiUrl}/${id}/`);
  }

  createMascota(mascota: MascotaPayload): Observable<Mascota> {
    return this.http.post<Mascota>(`${this.apiUrl}/`, mascota);
  }

  updateMascota(id: number, mascota: Partial<MascotaPayload>): Observable<Mascota> {
    return this.http.patch<Mascota>(`${this.apiUrl}/${id}/`, mascota);
  }

  deleteMascota(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }
}
