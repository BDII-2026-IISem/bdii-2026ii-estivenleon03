import { Status, Timestamps } from './api.model';

export interface Role extends Timestamps {
  id: number;
  name: string;
  description: string | null;
  status: Status;
}

export interface RolePayload {
  name: string;
  description: string | null;
  status: Status;
}
