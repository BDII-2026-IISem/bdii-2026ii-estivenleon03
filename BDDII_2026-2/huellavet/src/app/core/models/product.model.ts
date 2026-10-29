import { Money, Status, Timestamps } from './api.model';

export interface Product extends Timestamps {
  id: number;
  productTypeId: number;
  productTypeName?: string;
  name: string;
  brand: string;
  description: string | null;
  price: Money;
  minStock: number;
  quantity: number;
  status: Status;
}

export interface ProductPayload {
  productTypeId: number;
  name: string;
  brand: string;
  description: string | null;
  price: Money;
  minStock: number;
  quantity: number;
}
