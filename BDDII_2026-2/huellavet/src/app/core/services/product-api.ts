import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Status } from '../models/api.model';
import { Product, ProductPayload } from '../models/product.model';

@Injectable({ providedIn: 'root' })
export class ProductApi {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/vaccines`;

  list(status?: Status): Observable<Product[]> {
    const options = status ? { params: { status } } : {};
    return this.http.get<Product[]>(`${this.base}/`, options);
  }

  available(): Observable<Product[]> {
    return this.http.get<Product[]>(`${this.base}/available/`);
  }

  get(id: number): Observable<Product> {
    return this.http.get<Product>(`${this.base}/${id}/`);
  }

  create(payload: ProductPayload & { status: Status }): Observable<Product> {
    return this.http.post<Product>(`${this.base}/`, payload);
  }

  update(id: number, payload: Partial<ProductPayload>): Observable<Product> {
    return this.http.patch<Product>(`${this.base}/${id}/`, payload);
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/`);
  }
}
