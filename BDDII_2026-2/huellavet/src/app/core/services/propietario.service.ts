import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Propietario } from '../models/propietario.model';

@Injectable({
  providedIn: 'root'
})
export class PropietarioService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/owners/';

  getOwners(): Observable<Propietario[]> {
    return this.http.get<Propietario[]>(this.apiUrl);
  }

  getPropietarioById(id: number): Observable<Propietario> {
    return this.http.get<Propietario>(`${this.apiUrl}${id}/`);
  }

  createPropietario(propietario: Propietario): Observable<Propietario> {
    return this.http.post<Propietario>(this.apiUrl, propietario);
  }

  updatePropietario(id: number, propietario: Propietario): Observable<Propietario> {
    return this.http.put<Propietario>(`${this.apiUrl}${id}/`, propietario);
  }

  deletePropietario(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}
