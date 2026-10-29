import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Status } from '../models/api.model';
import { ProductType, ProductTypePayload } from '../models/product-type.model';

@Injectable({ providedIn: 'root' })
export class ProductTypeApi {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/product-types`;

  list(status?: Status): Observable<ProductType[]> {
    const options = status ? { params: { status } } : {};
    return this.http.get<ProductType[]>(`${this.base}/`, options);
  }

  get(id: number): Observable<ProductType> {
    return this.http.get<ProductType>(`${this.base}/${id}/`);
  }

  create(payload: ProductTypePayload & { status: Status }): Observable<ProductType> {
    return this.http.post<ProductType>(`${this.base}/`, payload);
  }

  update(
    id: number,
    payload: Partial<ProductTypePayload> & { status?: Status },
  ): Observable<ProductType> {
    return this.http.patch<ProductType>(`${this.base}/${id}/`, payload);
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/`);
  }
}
