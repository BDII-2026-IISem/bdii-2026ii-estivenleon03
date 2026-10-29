import { HttpClient } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface CrudApi<T, P> {
  list(): Observable<T[]>;
  create(payload: P): Observable<T>;
  update(id: number, payload: P): Observable<T>;
  remove(id: number): Observable<void>;
}

export abstract class CrudService<T, P> implements CrudApi<T, P> {
  protected readonly http = inject(HttpClient);
  protected readonly endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  list(): Observable<T[]> {
    return this.http.get<T[]>(`${this.endpoint}/`);
  }

  create(payload: P): Observable<T> {
    return this.http.post<T>(`${this.endpoint}/`, payload);
  }

  update(id: number, payload: P): Observable<T> {
    return this.http.patch<T>(`${this.endpoint}/${id}/`, payload);
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.endpoint}/${id}/`);
  }
}
