import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { SessionStore } from './session-store';

describe('SessionStore', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
  });

  it('debe comparar método y ruta, normalizando versión, barra final y parámetros', () => {
    const store = TestBed.inject(SessionStore);
    store.setTokens({ access: 'a', refresh: 'r' });
    store.setUser(
      { id: 1, username: 'admin', email: 'admin@test.com' },
      [
        { method: 'GET', path: '/api/v1/owners/', roleId: 1, roleName: 'ADMIN' },
        { method: 'PATCH', path: '/api/owners/:id', roleId: 1, roleName: 'ADMIN' },
      ]
    );

    expect(store.canPermission('GET /api/owners')).toBe(true);
    expect(store.canPermission('PATCH /api/owners/7')).toBe(true);
    expect(store.canPermission('DELETE /api/owners/7')).toBe(false);
    expect(store.roles()).toEqual(['ADMIN']);
  });

  it('debe reemplazar permisos previos cuando la respuesta actual viene vacía', () => {
    const store = TestBed.inject(SessionStore);
    const user = { id: 1, username: 'admin', email: 'admin@test.com' };

    store.setUser(user, [{ method: 'GET', path: '/api/owners', roleId: 1, roleName: 'ADMIN' }]);
    store.setUser(user, []);

    expect(store.canPermission('GET /api/owners')).toBe(false);
    expect(store.roles()).toEqual([]);
  });

  it('no debe asignar alias de endpoints que no están en los permisos', () => {
    const store = TestBed.inject(SessionStore);
    store.setTokens({ access: 'a', refresh: 'r' });
    store.setUser(
      { id: 2, username: 'operator', email: 'operator@test.com' },
      [
        {
          method: 'POST',
          path: '/api/v1/permissions/',
          roleId: 2,
          roleName: 'OPERATOR',
        },
      ]
    );

    expect(store.canPermission('POST /api/v1/permissions')).toBe(true);
    expect(store.canPermission('POST /api/resources')).toBe(false);
  });
});
