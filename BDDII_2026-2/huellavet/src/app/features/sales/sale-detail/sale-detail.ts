import { CurrencyPipe, DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ConfirmationService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { Sale } from '../../../core/models/sale.model';
import { NotificationService } from '../../../core/services/notification.service';
import { SaleApi } from '../../../core/services/sale-api';
import { toApiMessage } from '../../../core/utils/to-api-message';
import { PageHeader } from '../../../shared/ui/page-header/page-header';
import { StatusTag } from '../../../shared/ui/status-tag/status-tag';

@Component({
  selector: 'app-sale-detail',
  standalone: true,
  imports: [
    ButtonModule,
    CardModule,
    CurrencyPipe,
    DatePipe,
    MessageModule,
    PageHeader,
    RouterLink,
    StatusTag,
    TableModule,
    TagModule,
  ],
  templateUrl: './sale-detail.html',
  styleUrl: './sale-detail.css',
  host: { class: 'block' },
})
export class SaleDetail {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(SaleApi);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);

  readonly sale = signal<Sale | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly isVoided = computed(() => this.sale()?.status === 'inactive');

  constructor() {
    this.load();
  }

  load(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam) {
      this.error.set('Identificador de venta no válido.');
      this.loading.set(false);
      return;
    }

    const saleId = Number(idParam);
    this.loading.set(true);
    this.error.set(null);

    this.api.get(saleId).subscribe({
      next: (data) => {
        this.sale.set(data);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }

  voidSale(): void {
    const current = this.sale();
    if (!current || this.isVoided()) return;

    this.confirmation.confirm({
      header: 'Anular Venta',
      message: `¿Anular la venta #${current.id}? Se repondrán las unidades al stock en el servidor.`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Anular Venta',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.voidSale(current.id).subscribe({
          next: () => {
            this.notify.warn('Venta anulada');
            this.load();
          },
          error: (err: unknown) =>
            this.notify.error('No se pudo anular la venta', toApiMessage(err)),
        }),
    });
  }
}
