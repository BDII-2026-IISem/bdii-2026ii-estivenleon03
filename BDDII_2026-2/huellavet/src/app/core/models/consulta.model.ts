export interface Consulta {
  id?: number;
  mascota_id: number;
  mascota_nombre?: string;
  propietario_nombre?: string;
  motivo: string;
  fecha?: string | Date;
  estado: 'Pendiente' | 'Completada' | 'Cancelada';
}
