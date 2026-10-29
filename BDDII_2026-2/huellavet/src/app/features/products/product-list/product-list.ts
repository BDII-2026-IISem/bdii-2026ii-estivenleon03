import { CurrencyPipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import { ConfirmationService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { SelectModule } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { ProductType } from '../../../core/models/product-type.model';
import { Product, ProductPayload } from '../../../core/models/product.model';
import { NotificationService } from '../../../core/services/notification.service';
import { ProductApi } from '../../../core/services/product-api';
import { ProductTypeApi } from '../../../core/services/product-type-api';
import { toApiMessage } from '../../../core/utils/to-api-message';
import { filterRows } from '../../../core/utils/filter-rows';
import { EmptyState } from '../../../shared/ui/empty-state/empty-state';
import { PageHeader } from '../../../shared/ui/page-header/page-header';
import { StatusTag } from '../../../shared/ui/status-tag/status-tag';
import { ProductForm } from '../product-form/product-form';

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [
    ButtonModule,
    CurrencyPipe,
    DialogModule,
    EmptyState,
    InputTextModule,
    MessageModule,
    PageHeader,
    SelectModule,
    StatusTag,
    TableModule,
    TagModule,
    TooltipModule,
    ProductForm,
  ],
  templateUrl: './product-list.html',
  styleUrl: './product-list.css',
  host: { class: 'block' },
})
export class ProductList {
  private readonly api = inject(ProductApi);
  private readonly typesApi = inject(ProductTypeApi);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);

  readonly rows = signal<Product[]>([]);
  readonly types = signal<ProductType[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly filter = signal('');
  readonly onlyAvailable = signal(false);
  readonly statusFilter = signal<'all' | 'active' | 'inactive'>('active');
  readonly typeFilter = signal('all');
  readonly dialogVisible = signal(false);
  readonly editing = signal<Product | null>(null);
  readonly resetKey = signal(0);

  readonly lowStock = computed(() =>
    new Set(
      this.rows()
        .filter((p) => p.status === 'active' && p.quantity <= p.minStock)
        .map((p) => p.id)
    )
  );

  readonly activeCount = computed(() => this.rows().filter((p) => p.status === 'active').length);
  readonly outOfStockCount = computed(
    () => this.rows().filter((p) => p.status === 'active' && p.quantity === 0).length
  );
  readonly inventoryValue = computed(() =>
    this.rows()
      .filter((p) => p.status === 'active')
      .reduce((total, p) => total + Number(p.price) * p.quantity, 0)
  );
  readonly visibleTypes = computed(() =>
    this.types().filter((type) => type.status === 'active')
  );
  readonly statusRows = computed(() => {
    const status = this.statusFilter();
    const typeId = this.typeFilter();
    return this.rows().filter(
      (product) =>
        (status === 'all' || product.status === status) &&
        (typeId === 'all' || product.productTypeId === Number(typeId)) &&
        (!this.onlyAvailable() ||
          (product.status === 'active' &&
            product.quantity > 0 &&
            this.visibleTypes().some((type) => type.id === product.productTypeId)))
    );
  });
  readonly visibleRows = computed(() =>
    filterRows(this.statusRows(), this.filter(), (p) => [
      p.name,
      p.brand,
      p.description,
      p.productTypeName,
    ])
  );

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);

    forkJoin({
      products: this.api.list(),
      types: this.typesApi.list('active'),
    }).subscribe({
      next: ({ products, types }) => {
        this.rows.set(products);
        this.types.set(types);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.rows.set([]);
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }

  toggleAvailable(): void {
    this.onlyAvailable.update((v) => !v);
  }

  openCreate(): void {
    this.editing.set(null);
    this.resetKey.update((k) => k + 1);
    this.dialogVisible.set(true);
  }

  openEdit(product: Product): void {
    this.editing.set(product);
    this.resetKey.update((k) => k + 1);
    this.dialogVisible.set(true);
  }

  save(payload: ProductPayload): void {
    const current = this.editing();
    this.saving.set(true);
    const request = current
      ? this.api.update(current.id, payload)
      : this.api.create({ ...payload, status: 'active' });

    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success(current ? 'Producto actualizado' : 'Producto creado');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar', toApiMessage(err));
      },
    });
  }

  remove(product: Product): void {
    this.confirmation.confirm({
      header: 'Dar de baja',
      message: `¿Desactivar «${product.name}»? Dejará de operar en el inventario.`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Desactivar',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.remove(product.id).subscribe({
          next: () => {
            this.notify.warn('Producto desactivado');
            this.load();
          },
          error: (err: unknown) => this.notify.error('No se pudo desactivar', toApiMessage(err)),
        }),
    });
  }

  reactivate(product: Product): void {
    this.confirmation.confirm({
      header: 'Reactivar producto',
      message: `¿Reactivar «${product.name}»? Volverá a aparecer en el inventario activo.`,
      icon: 'pi pi-refresh',
      acceptLabel: 'Reactivar',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.update(product.id, { status: 'active' }).subscribe({
          next: () => {
            this.notify.success('Producto reactivado');
            this.load();
          },
          error: (err: unknown) =>
            this.notify.error('No se pudo reactivar', toApiMessage(err)),
        }),
    });
  }
}
