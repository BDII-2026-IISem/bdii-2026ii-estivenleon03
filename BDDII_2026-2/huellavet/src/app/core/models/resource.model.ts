import { HttpMethod, Status, Timestamps } from './api.model';

export interface Resource extends Timestamps {
  id: number;
  method: HttpMethod;
  path: string;
  description: string | null;
  status: Status;
}

export interface ResourcePayload {
  method: HttpMethod;
  path: string;
  description: string | null;
  status: Status;
}
