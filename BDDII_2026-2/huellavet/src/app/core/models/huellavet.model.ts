export interface Owner {
  id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  doc_type: string;
  doc_number: string;
  name: string;
  phone: string;
  email: string;
}

export interface Pet {
  id: number;
  owner_details: Owner;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  name: string;
  species: string;
  breed: string;
  birth_date?: string;
}

export interface Payment {
  id: number;
  reference_type: string;
  reference_id: number;
  method: string;
  amount: string; // Decimal string desde Django ("120000.00")
  payment_date: string;
  status: string;
  appointment?: number;
}