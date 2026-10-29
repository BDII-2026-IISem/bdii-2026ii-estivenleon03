import { CurrencyPipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { Propietario } from '../../core/models/propietario.model';
import { Product } from '../../core/models/product.model';
import { Sale } from '../../core/models/sale.model';
import { toNumber } from '../../core/models/api.model';
import { PropietarioApi } from '../../core/services/propietario-api';
import { ProductApi } from '../../core/services/product-api';
import { SaleApi } from '../../core/services/sale-api';
import { toApiMessage } from '../../core/utils/to-api-message';
import { EmptyState } from '../../shared/ui/empty-state/empty-state';
import { PageHeader } from '../../shared/ui/page-header/page-header';

function sameDay(iso: string, reference: Date): boolean {
  const date = new Date(iso);
  return (
    date.getFullYear() === reference.getFullYear() &&
    date.getMonth() === reference.getMonth() &&
    date.getDate() === reference.getDate()
  );
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    ButtonModule,
    CardModule,
    CurrencyPipe,
    EmptyState,
    MessageModule,
    PageHeader,
    TableModule,
    TagModule,
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
  host: { class: 'block' },
})
export class Dashboard {
  private readonly paymentsApi = inject(SaleApi);
  private readonly productsApi = inject(ProductApi);
  private readonly clientsApi = inject(PropietarioApi);

  readonly payments = signal<Sale[]>([]);
  readonly products = signal<Product[]>([]);
  readonly clients = signal<Propietario[]>([]);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly todayPayments = computed(() => {
    const now = new Date();
    return this.payments().filter((s) => s.status === 'active' && sameDay(s.saleDate, now));
  });

  readonly todayTotal = computed(() =>
    this.todayPayments().reduce((acc, s) => acc + toNumber(s.total), 0)
  );

  readonly lowStockProducts = computed(() =>
    this.products().filter((p) => p.status === 'active' && p.quantity <= p.minStock)
  );

  readonly activeClientsCount = computed(
    () => this.clients().filter((c) => c.status === 'active').length
  );

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);

    forkJoin({
      payments: this.paymentsApi.list(),
      products: this.productsApi.list('active'),
      clients: this.clientsApi.list(),
    }).subscribe({
      next: ({ payments, products, clients }) => {
        this.payments.set(payments);
        this.products.set(products);
        this.clients.set(clients);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }
}
