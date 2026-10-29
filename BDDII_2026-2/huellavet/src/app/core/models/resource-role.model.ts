import { Status, Timestamps } from './api.model';

export interface ResourceRole extends Timestamps {
  id: number;
  role_id?: number;
  roleId?: number;
  role?: number | { id: number; name: string };
  permission_id?: number;
  resourceId?: number;
  permission?: number | { id: number; code: string; name: string };
  status: Status;
}

export interface ResourceRolePayload {
  role_id?: number;
  roleId?: number;
  permission_id?: number;
  resourceId?: number;
  status: Status;
}
