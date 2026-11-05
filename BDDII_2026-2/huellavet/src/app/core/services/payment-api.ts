import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Sale, SalePaymentCreatePayload } from '../models/sale.model';

@Injectable({ providedIn: 'root' })
export class PaymentApi {
  private readonly http = inject(HttpClient);
  private readonly salesBase = `${environment.apiUrl}/sales`;

  addSalePayment(saleId: number, payload: SalePaymentCreatePayload): Observable<Sale> {
    return this.http.post<Sale>(`${this.salesBase}/${saleId}/payments/`, payload);
  }
}
