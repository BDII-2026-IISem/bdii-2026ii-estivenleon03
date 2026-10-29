export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
export type Status = 'active' | 'inactive';

export interface Timestamps {
  createdAt?: string;
  updatedAt?: string;
}

export type Money = string;

export function toNumber(value: Money | number | null | undefined): number {
  if (typeof value === 'number') return value;
  if (!value) return 0;
  const parsed = parseFloat(value);
  return isNaN(parsed) ? 0 : parsed;
}

export const STATUS_OPTIONS: Array<{ label: string; value: Status }> = [
  { label: 'Activo', value: 'active' },
  { label: 'Inactivo', value: 'inactive' },
];
