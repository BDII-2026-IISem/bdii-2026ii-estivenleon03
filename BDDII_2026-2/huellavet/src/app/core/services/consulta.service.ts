import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Consulta, ConsultaPayload } from '../models/consulta.model';

@Injectable({
  providedIn: 'root'
})
export class ConsultaService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/consultations`;

  getConsultas(): Observable<Consulta[]> {
    return this.http.get<Consulta[]>(`${this.apiUrl}/`);
  }

  getConsultaById(id: number): Observable<Consulta> {
    return this.http.get<Consulta>(`${this.apiUrl}/${id}/`);
  }

  createConsulta(consulta: ConsultaPayload): Observable<Consulta> {
    return this.http.post<Consulta>(`${this.apiUrl}/`, consulta);
  }

  updateConsulta(id: number, consulta: Partial<ConsultaPayload>): Observable<Consulta> {
    return this.http.patch<Consulta>(`${this.apiUrl}/${id}/`, consulta);
  }

  deleteConsulta(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }
}
