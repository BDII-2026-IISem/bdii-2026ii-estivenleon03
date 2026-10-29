import { CurrencyPipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { FlatSaleLine, ProductSaleApi } from '../../../core/services/product-sale-api';
import { toApiMessage } from '../../../core/utils/to-api-message';
import { filterRows } from '../../../core/utils/filter-rows';
import { EmptyState } from '../../../shared/ui/empty-state/empty-state';
import { PageHeader } from '../../../shared/ui/page-header/page-header';

@Component({
  selector: 'app-product-sale-list',
  standalone: true,
  imports: [
    ButtonModule,
    CurrencyPipe,
    EmptyState,
    InputTextModule,
    MessageModule,
    PageHeader,
    RouterLink,
    TableModule,
    TagModule,
  ],
  templateUrl: './product-sale-list.html',
  styleUrl: './product-sale-list.css',
  host: { class: 'block' },
})
export class ProductSaleList {
  private readonly api = inject(ProductSaleApi);

  readonly rows = signal<FlatSaleLine[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly filter = signal('');

  readonly totalUnits = computed(() =>
    this.rows().reduce((acc, line) => acc + line.quantity, 0)
  );

  readonly visibleRows = computed(() =>
    filterRows(this.rows(), this.filter(), (line) => [
      line.saleId,
      line.productName,
      line.quantity,
    ])
  );

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);

    this.api.list().subscribe({
      next: (data) => {
        this.rows.set(data);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.rows.set([]);
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }
}
