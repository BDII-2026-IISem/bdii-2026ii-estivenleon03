import { Status, Timestamps } from './api.model';

export interface RoleUser extends Timestamps {
  id: number;
  user_id?: number;
  userId?: number;
  user?: number | { id: number; username: string };
  role_id?: number;
  roleId?: number;
  role?: number | { id: number; name: string };
  status: Status;
}

export interface RoleUserPayload {
  user_id?: number;
  userId?: number;
  role_id?: number;
  roleId?: number;
  status: Status;
}
