import { HttpMethod } from '../models/api.model';

export const HTTP_METHODS: HttpMethod[] = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];

const SEVERITY: Record<HttpMethod, 'info' | 'success' | 'warn' | 'danger'> = {
  GET: 'info',
  POST: 'success',
  PUT: 'warn',
  PATCH: 'warn',
  DELETE: 'danger',
};

export const methodSeverity = (method?: HttpMethod) => (method ? SEVERITY[method] : 'secondary');
