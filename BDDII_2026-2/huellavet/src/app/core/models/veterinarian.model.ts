export interface Veterinarian {
  id: number;
  name: string;
  license_number: string | null;
  description: string | null;
  is_active: boolean;
  auth_user: number | null;
  auth_user_details: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  } | null;
}

export type VeterinarianPayload = Omit<Veterinarian, 'id' | 'auth_user_details'>;
