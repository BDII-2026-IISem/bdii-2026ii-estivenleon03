import { CurrencyPipe, DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { Propietario } from '../../../core/models/propietario.model';
import { Product } from '../../../core/models/product.model';
import { Sale, SaleCreatePayload } from '../../../core/models/sale.model';
import { NotificationService } from '../../../core/services/notification.service';
import { PropietarioApi } from '../../../core/services/propietario-api';
import { ProductApi } from '../../../core/services/product-api';
import { SaleApi } from '../../../core/services/sale-api';
import { toApiMessage } from '../../../core/utils/to-api-message';
import { filterRows } from '../../../core/utils/filter-rows';
import { EmptyState } from '../../../shared/ui/empty-state/empty-state';
import { PageHeader } from '../../../shared/ui/page-header/page-header';
import { StatusTag } from '../../../shared/ui/status-tag/status-tag';
import { SaleForm } from '../sale-form/sale-form';

@Component({
  selector: 'app-sale-list',
  standalone: true,
  imports: [
    ButtonModule,
    CurrencyPipe,
    DatePipe,
    DialogModule,
    EmptyState,
    InputTextModule,
    MessageModule,
    PageHeader,
    RouterLink,
    StatusTag,
    TableModule,
    TagModule,
    TooltipModule,
    SaleForm,
  ],
  templateUrl: './sale-list.html',
  styleUrl: './sale-list.css',
  host: { class: 'block' },
})
export class SaleList {
  private readonly api = inject(SaleApi);
  private readonly clientsApi = inject(PropietarioApi);
  private readonly productsApi = inject(ProductApi);
  private readonly notify = inject(NotificationService);

  readonly rows = signal<Sale[]>([]);
  readonly clients = signal<Propietario[]>([]);
  readonly products = signal<Product[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly serverError = signal<string | null>(null);
  readonly filter = signal('');
  readonly dialogVisible = signal(false);
  readonly resetKey = signal(0);

  readonly totalAvailableStock = computed(() =>
    this.products().reduce((acc, p) => acc + p.quantity, 0)
  );

  readonly clientsMap = computed(() => {
    const map = new Map<number, string>();
    this.clients().forEach((c) => map.set(c.id, c.nombre));
    return map;
  });

  readonly visibleRows = computed(() =>
    filterRows(this.rows(), this.filter(), (s) => [
      s.id,
      s.clientName || this.clientsMap().get(s.client) || `Cliente #${s.client}`,
      s.total,
    ])
  );

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);

    forkJoin({
      payments: this.api.list(),
      clients: this.clientsApi.list(),
      products: this.productsApi.available(),
    }).subscribe({
      next: ({ payments, clients, products }) => {
        this.rows.set(payments);
        this.clients.set(clients.filter((c) => c.status === 'active'));
        this.products.set(products);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.rows.set([]);
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.serverError.set(null);
    this.resetKey.update((k) => k + 1);
    this.dialogVisible.set(true);
  }

  save(payload: SaleCreatePayload): void {
    this.saving.set(true);
    this.serverError.set(null);

    this.api.create(payload).subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success('Venta registrada con éxito');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.serverError.set(toApiMessage(err));
      },
    });
  }

  getClientDisplayName(sale: Sale): string {
    return sale.clientName || this.clientsMap().get(sale.client) || `Propietario #${sale.client}`;
  }
}
