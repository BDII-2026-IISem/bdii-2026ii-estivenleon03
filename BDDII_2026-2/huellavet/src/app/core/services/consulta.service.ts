import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Consulta } from '../models/consulta.model';

@Injectable({
  providedIn: 'root'
})
export class ConsultaService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/consultas/';

  getConsultas(): Observable<Consulta[]> {
    return this.http.get<Consulta[]>(this.apiUrl);
  }

  getConsultaById(id: number): Observable<Consulta> {
    return this.http.get<Consulta>(`${this.apiUrl}${id}/`);
  }

  createConsulta(consulta: Consulta): Observable<Consulta> {
    return this.http.post<Consulta>(this.apiUrl, consulta);
  }

  updateConsulta(id: number, consulta: Consulta): Observable<Consulta> {
    return this.http.put<Consulta>(`${this.apiUrl}${id}/`, consulta);
  }

  deleteConsulta(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}
