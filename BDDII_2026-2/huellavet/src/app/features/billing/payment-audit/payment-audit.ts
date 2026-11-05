import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { MessageModule } from 'primeng/message';
import { InputTextModule } from 'primeng/inputtext';
import { TagModule } from 'primeng/tag';
import { PaymentAudit } from '../../../core/models/payment.model';
import { AppointmentPaymentApi } from '../../../core/services/appointment-payment-api';
import { toApiMessage } from '../../../core/utils/to-api-message';
import { PageHeader } from '../../../shared/ui/page-header/page-header';

type AuditAction = PaymentAudit['actionSale'];

interface AuditField {
  label: string;
  value: string;
}

@Component({
  selector: 'app-payment-audit',
  standalone: true,
  imports: [
    ButtonModule,
    FormsModule,
    InputTextModule,
    MessageModule,
    PageHeader,
    TagModule,
  ],
  templateUrl: './payment-audit.html',
  host: { class: 'block' },
})
export class PaymentAuditPage {
  private readonly api = inject(AppointmentPaymentApi);

  readonly rows = signal<PaymentAudit[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly filter = signal('');
  readonly filteredRows = computed(() => {
    const query = this.filter().trim().toLocaleLowerCase();
    if (!query) return this.rows();
    return this.rows().filter((entry) =>
      [entry.actionSale, entry.payment_id, entry.changed_by, entry.changed_at]
        .some((value) => String(value).toLocaleLowerCase().includes(query))
    );
  });
  readonly insertCount = computed(() =>
    this.rows().filter((entry) => entry.actionSale === 'INSERT').length
  );
  readonly updateCount = computed(() =>
    this.rows().filter((entry) => entry.actionSale === 'UPDATE').length
  );
  readonly deleteCount = computed(() =>
    this.rows().filter((entry) => entry.actionSale === 'DELETE').length
  );

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.listAudits().subscribe({
      next: (rows) => {
        this.rows.set(rows);
        this.loading.set(false);
      },
      error: (err: unknown) => {
        this.error.set(toApiMessage(err));
        this.loading.set(false);
      },
    });
  }

  actionLabel(action: AuditAction): string {
    return {
      INSERT: 'Creación',
      UPDATE: 'Actualización',
      DELETE: 'Eliminación',
    }[action];
  }

  actionIcon(action: AuditAction): string {
    return {
      INSERT: 'pi pi-plus',
      UPDATE: 'pi pi-pencil',
      DELETE: 'pi pi-trash',
    }[action];
  }

  actionSeverity(action: AuditAction): 'success' | 'info' | 'danger' {
    switch (action) {
      case 'INSERT':
        return 'success';
      case 'UPDATE':
        return 'info';
      case 'DELETE':
        return 'danger';
    }
  }

  formatDate(value: string): string {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat('es-CO', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(date);
  }

  auditFields(data: Record<string, unknown> | null): AuditField[] {
    if (!data) return [];
    return Object.entries(data)
      .filter(([key]) => key !== 'id')
      .map(([key, value]) => ({
        label: this.fieldLabel(key),
        value: this.formatFieldValue(key, value),
      }));
  }

  private fieldLabel(key: string): string {
    const labels: Record<string, string> = {
      amount: 'Monto',
      method: 'Medio de pago',
      status: 'Estado',
      payment_date: 'Fecha del pago',
      appointment_id: 'Cita asociada',
    };
    return labels[key] ?? key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (letter) => letter.toLocaleUpperCase());
  }

  private formatFieldValue(key: string, value: unknown): string {
    if (value === null || value === undefined || value === '') return 'No especificado';

    if (key === 'amount') {
      const amount = Number(value);
      if (Number.isFinite(amount)) {
        return new Intl.NumberFormat('es-CO', {
          style: 'currency',
          currency: 'COP',
          maximumFractionDigits: 0,
        }).format(amount);
      }
    }

    if (key === 'payment_date' && typeof value === 'string') {
      return this.formatDate(value.replace(' ', 'T'));
    }

    if (key === 'method' && typeof value === 'string') {
      const methods: Record<string, string> = {
        CASH: 'Efectivo',
        DEBIT_CARD: 'Tarjeta débito',
        CREDIT_CARD: 'Tarjeta crédito',
        TRANSFER: 'Transferencia',
      };
      return methods[value] ?? value;
    }

    if (key === 'status' && typeof value === 'string') {
      const statuses: Record<string, string> = {
        PENDING: 'Pendiente',
        PAID: 'Pagado',
        CANCELLED: 'Cancelado',
      };
      return statuses[value] ?? value;
    }

    if (key.endsWith('_id') && typeof value === 'number') return `#${value}`;
    if (typeof value === 'boolean') return value ? 'Sí' : 'No';
    if (typeof value === 'object') return 'Información adicional disponible';
    return String(value);
  }
}
