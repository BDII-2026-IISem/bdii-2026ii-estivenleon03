import { Money } from './api.model';

export type AppointmentPaymentMethod = 'CASH' | 'DEBIT_CARD' | 'CREDIT_CARD' | 'TRANSFER';
export type AppointmentPaymentStatus = 'PENDING' | 'PAID' | 'CANCELLED';

export interface AppointmentPayment {
  id: number;
  appointment: number;
  reference_type: string;
  reference_id: number;
  method: AppointmentPaymentMethod;
  amount: Money;
  payment_date: string | null;
  status: AppointmentPaymentStatus;
}

export interface AppointmentPaymentPayload {
  appointment: number;
  reference_type: string;
  reference_id: number;
  method: AppointmentPaymentMethod;
  amount: Money;
  status: AppointmentPaymentStatus;
}

export interface PaymentAudit {
  id: number;
  payment_id: number;
  actionSale: 'INSERT' | 'UPDATE' | 'DELETE';
  changed_at: string;
  changed_by: string;
  before_data: Record<string, unknown> | null;
  after_data: Record<string, unknown> | null;
}
