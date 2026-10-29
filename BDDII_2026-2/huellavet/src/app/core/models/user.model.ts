import { Status, Timestamps } from './api.model';

export interface User extends Timestamps {
  id: number;
  username: string;
  email: string;
  avatar: string | null;
  status: Status;
}

export interface UserPayload {
  username: string;
  email: string;
  avatar: string | null;
  status: Status;
  password?: string;
}
