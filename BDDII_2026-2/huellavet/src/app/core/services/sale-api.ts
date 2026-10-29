import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Sale, SaleCreatePayload } from '../models/sale.model';

@Injectable({ providedIn: 'root' })
export class SaleApi {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/payments`;

  list(): Observable<Sale[]> {
    return this.http.get<Sale[]>(`${this.base}/`);
  }

  get(id: number): Observable<Sale> {
    return this.http.get<Sale>(`${this.base}/${id}/`);
  }

  create(payload: SaleCreatePayload): Observable<Sale> {
    return this.http.post<Sale>(`${this.base}/`, payload);
  }

  voidSale(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/`);
  }
}
