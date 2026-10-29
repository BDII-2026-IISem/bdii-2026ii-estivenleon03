export interface Prescription {
  id: number;
  consultation: number;
  medication_name: string;
  description: string | null;
  dosage: string;
  frequency: string;
  duration_days: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export type PrescriptionPayload = Omit<Prescription, 'id' | 'created_at' | 'updated_at'>;

export interface Vaccine {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
}

export interface VaccineBatch {
  id: number;
  vaccine: number;
  name: string;
  batch_number: string;
  description: string | null;
  expiration_date: string;
  stock_quantity: number;
  is_active: boolean;
}

export interface VaccineApplication {
  id: number;
  consultation: number;
  vaccine_batch: number;
  name: string;
  description: string | null;
  dosage_ml: string | number;
  notes: string | null;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export type VaccineApplicationPayload = Omit<
  VaccineApplication,
  'id' | 'created_at' | 'updated_at'
>;
