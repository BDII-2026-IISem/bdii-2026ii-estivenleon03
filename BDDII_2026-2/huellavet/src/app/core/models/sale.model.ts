import { Money, Status, Timestamps } from './api.model';

export interface SaleItemLine {
  productId: number;
  productName?: string;
  quantity: number;
  unitPrice: Money;
  lineTotal: Money;
}

export type PaymentMethod = 'CASH' | 'DEBIT_CARD' | 'CREDIT_CARD' | 'TRANSFER';

export interface SalePayment {
  id: number;
  method: PaymentMethod;
  amount: Money;
  paymentDate: string | null;
  status: 'PENDING' | 'PAID' | 'CANCELLED';
}

export interface Sale extends Timestamps {
  id: number;
  client: number;
  clientName?: string;
  pet?: number | null;
  petName?: string | null;
  saleDate: string;
  subtotal: Money;
  tax: Money;
  discounts: Money;
  total: Money;
  status: Status;
  paymentStatus?: 'PENDING' | 'PARTIAL' | 'PAID' | 'CANCELLED';
  items?: SaleItemLine[];
  payments?: SalePayment[];
  paidAmount?: Money;
  balanceDue?: Money;
}

export interface SalePaymentCreatePayload {
  method: PaymentMethod;
  amount: Money;
}

export interface SaleCreatePayload {
  clientId: number;
  petId?: number | null;
  saleDate: string;
  discounts: Money;
  items: { productId: number; quantity: number }[];
  paymentMethod?: PaymentMethod | null;
  paymentAmount?: Money | null;
}
