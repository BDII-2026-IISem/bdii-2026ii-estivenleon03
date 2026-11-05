import { CurrencyPipe, DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ConfirmationService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import {
  AppointmentPayment,
  AppointmentPaymentMethod,
  AppointmentPaymentPayload,
  AppointmentPaymentStatus,
} from '../../../core/models/payment.model';
import { Appointment } from '../../../core/models/appointment.model';
import { AppointmentApi } from '../../../core/services/appointment-api';
import { NotificationService } from '../../../core/services/notification.service';
import { AppointmentPaymentApi } from '../../../core/services/appointment-payment-api';
import { SessionStore } from '../../../core/services/session-store';
import { toApiMessage } from '../../../core/utils/to-api-message';
import { HasPermission } from '../../../shared/directives/has-permission';
import { PageHeader } from '../../../shared/ui/page-header/page-header';

@Component({
  selector: 'app-appointment-payments',
  standalone: true,
  imports: [
    ButtonModule,
    CurrencyPipe,
    DatePipe,
    DialogModule,
    FormsModule,
    HasPermission,
    MessageModule,
    PageHeader,
    TableModule,
    TagModule,
  ],
  templateUrl: './appointment-payments.html',
  host: { class: 'block' },
})
export class AppointmentPayments {
  private readonly api = inject(AppointmentPaymentApi);
  private readonly appointmentsApi = inject(AppointmentApi);
  private readonly session = inject(SessionStore);
  private readonly notify = inject(NotificationService);
  private readonly confirmation = inject(ConfirmationService);

  readonly rows = signal<AppointmentPayment[]>([]);
  readonly appointments = signal<Appointment[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly dialogVisible = signal(false);
  readonly editing = signal<AppointmentPayment | null>(null);
  readonly canReadAppointments = signal(false);

  current: AppointmentPaymentPayload = this.emptyForm();
  readonly methods: Array<{ label: string; value: AppointmentPaymentMethod }> = [
    { label: 'Efectivo', value: 'CASH' },
    { label: 'Tarjeta débito', value: 'DEBIT_CARD' },
    { label: 'Tarjeta crédito', value: 'CREDIT_CARD' },
    { label: 'Transferencia', value: 'TRANSFER' },
  ];
  readonly statuses: Array<{ label: string; value: AppointmentPaymentStatus }> = [
    { label: 'Pendiente', value: 'PENDING' },
    { label: 'Pagado', value: 'PAID' },
    { label: 'Cancelado', value: 'CANCELLED' },
  ];

  constructor() {
    this.canReadAppointments.set(this.session.canPermission('GET /api/v1/appointments'));
    if (this.canReadAppointments()) this.loadAppointments();
    this.load();
  }

  loadAppointments(): void {
    this.appointmentsApi.list().subscribe({
      next: (appointments) => this.appointments.set(appointments),
      error: (err: unknown) =>
        this.notify.error('No se pudieron cargar las citas', toApiMessage(err)),
    });
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.list().subscribe({
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

  openCreate(): void {
    if (!this.canReadAppointments() || this.appointments().length === 0) {
      this.notify.warn(
        'No hay citas disponibles',
        'Se requiere permiso de lectura y al menos una cita para registrar un pago.'
      );
      return;
    }
    this.editing.set(null);
    this.current = this.emptyForm();
    this.dialogVisible.set(true);
  }

  openEdit(payment: AppointmentPayment): void {
    this.editing.set(payment);
    this.current = {
      appointment: payment.appointment,
      reference_type: payment.reference_type,
      reference_id: payment.reference_id,
      method: payment.method,
      amount: payment.amount,
      status: payment.status,
    };
    this.dialogVisible.set(true);
  }

  save(): void {
    const appointmentId = Number(this.current.appointment);
    const amount = Number(this.current.amount);
    if (!Number.isInteger(appointmentId) || appointmentId <= 0 ||
        !Number.isFinite(amount) || amount <= 0) {
      this.notify.warn('Datos no válidos', 'Indica una cita existente y un monto positivo.');
      return;
    }

    const payload: AppointmentPaymentPayload = {
      ...this.current,
      appointment: appointmentId,
      reference_type: 'APPOINTMENT',
      reference_id: appointmentId,
      amount: amount.toFixed(2),
    };
    const existing = this.editing();
    this.saving.set(true);
    const request = existing
      ? this.api.update(existing.id, payload)
      : this.api.create(payload);

    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogVisible.set(false);
        this.notify.success(existing ? 'Pago actualizado' : 'Pago registrado');
        this.load();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.notify.error('No se pudo guardar el pago', toApiMessage(err));
      },
    });
  }

  remove(payment: AppointmentPayment): void {
    this.confirmation.confirm({
      header: 'Eliminar pago',
      message: `¿Eliminar el pago #${payment.id}? El historial de auditoría se conserva mediante el registro del servidor.`,
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Eliminar pago',
      rejectLabel: 'Cancelar',
      accept: () =>
        this.api.remove(payment.id).subscribe({
          next: () => {
            this.notify.warn('Pago eliminado');
            this.load();
          },
          error: (err: unknown) =>
            this.notify.error('No se pudo eliminar el pago', toApiMessage(err)),
        }),
    });
  }

  statusSeverity(status: AppointmentPaymentStatus): 'success' | 'warn' | 'danger' {
    if (status === 'PAID') return 'success';
    if (status === 'PENDING') return 'warn';
    return 'danger';
  }

  appointmentLabel(id: number): string {
    const appointment = this.appointments().find((item) => item.id === id);
    if (!appointment) return `Cita #${id}`;
    const patient = appointment.pet_details?.name ?? `Mascota #${appointment.pet}`;
    const veterinarian =
      appointment.veterinarian_details?.name ?? `Veterinario #${appointment.veterinarian}`;
    const date = new Intl.DateTimeFormat('es-CO', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(appointment.start_time));
    return `#${appointment.id} · ${patient} · ${veterinarian} · ${date}`;
  }

  methodLabel(method: AppointmentPaymentMethod): string {
    return {
      CASH: 'Efectivo',
      DEBIT_CARD: 'Tarjeta débito',
      CREDIT_CARD: 'Tarjeta crédito',
      TRANSFER: 'Transferencia',
    }[method];
  }

  statusLabel(status: AppointmentPaymentStatus): string {
    return {
      PENDING: 'Pendiente',
      PAID: 'Pagado',
      CANCELLED: 'Cancelado',
    }[status];
  }

  private emptyForm(): AppointmentPaymentPayload {
    return {
      appointment: 0,
      reference_type: 'APPOINTMENT',
      reference_id: 0,
      method: 'CASH',
      amount: '',
      status: 'PAID',
    };
  }
}
