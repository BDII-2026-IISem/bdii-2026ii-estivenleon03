import { Status, Timestamps } from './api.model';

export interface Propietario extends Timestamps {
  id: number;
  nombre: string;
  documento: string | null;
  telefono: string | null;
  email: string | null;
  direccion: string | null;
  status: Status;
}

export interface PropietarioPayload {
  nombre: string;
  documento: string | null;
  telefono: string | null;
  email: string | null;
  direccion: string | null;
}
