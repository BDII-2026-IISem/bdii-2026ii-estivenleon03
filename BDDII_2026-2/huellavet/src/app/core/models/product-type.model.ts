import { Status, Timestamps } from './api.model';

export interface ProductType extends Timestamps {
  id: number;
  name: string;
  description: string | null;
  status: Status;
}

export interface ProductTypePayload {
  name: string;
  description: string | null;
}
