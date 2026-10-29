export interface Mascota {
  id?: number;
  nombre: string;
  especie: string;
  raza: string;
  edad: string;
  propietario_id: number;
  propietario_nombre?: string;
  is_active: boolean;
}
