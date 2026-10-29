export interface Consulta {
  id: number;
  pet: number;
  veterinarian: number;
  appointment: number | null;
  title: string;
  description: string | null;
  temperature_c: string | number | null;
  weight_kg: string | number | null;
  heart_rate: number | null;
  symptoms: string;
  diagnosis: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export type ConsultaPayload = Omit<Consulta, 'id' | 'created_at' | 'updated_at'>;
