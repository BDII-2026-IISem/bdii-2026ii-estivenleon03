import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { SaleItemLine } from '../models/sale.model';
import { Sale } from '../models/sale.model';

export interface FlatSaleLine extends SaleItemLine {
  saleId: number;
}

@Injectable({ providedIn: 'root' })
export class ProductSaleApi {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/payments`;

  list(): Observable<FlatSaleLine[]> {
    return this.http.get<Sale[]>(`${this.base}/`).pipe(
      map((payments) =>
        payments.flatMap((s) =>
          (s.items ?? []).map((item) => ({
            saleId: s.id,
            ...item,
          }))
        )
      )
    );
  }
}
