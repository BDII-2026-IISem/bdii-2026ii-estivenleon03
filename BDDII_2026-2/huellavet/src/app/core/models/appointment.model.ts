export type AppointmentStatus =
  | 'SCHEDULED'
  | 'CONFIRMED'
  | 'IN_CONSULTATION'
  | 'COMPLETED'
  | 'CANCELLED';

export interface Appointment {
  id: number;
  pet: number;
  veterinarian: number;
  start_time: string;
  end_time: string;
  reason: string;
  status: AppointmentStatus;
  pet_details?: { id: number; name: string; owner: number; species: string | null };
  veterinarian_details?: { id: number; name: string };
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export type AppointmentPayload = Omit<
  Appointment,
  'id' | 'pet_details' | 'veterinarian_details' | 'created_at' | 'updated_at'
>;
