export interface Mascota {
  id: number;
  owner: number;
  name: string;
  species: string | null;
  breed: string | null;
  birth_date: string | null;
  gender: 'MALE' | 'FEMALE' | null;
  description: string | null;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export type MascotaPayload = Omit<Mascota, 'id' | 'created_at' | 'updated_at'>;
