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

  it('debe validar canPermission con rutas dinámicas :id y tolera la barra final', () => {
    const store = TestBed.inject(SessionStore);
    store.setTokens({ access: 'a', refresh: 'r', tokenType: 'Bearer', accessExpiresIn: 3600 });
    store.setUser(
      { id: 1, username: 'admin', email: 'admin@test.com', avatar: null, status: 'active' },
      [
        { method: 'GET', path: '/api/owners/', roleId: 1, roleName: 'ADMIN' },
        { method: 'PATCH', path: '/api/owners/:id', roleId: 1, roleName: 'ADMIN' },
      ]
    );

    expect(store.canPermission('GET /api/owners')).toBe(true);
    expect(store.canPermission('PATCH /api/owners/7')).toBe(true);
    expect(store.canPermission('DELETE /api/owners/7')).toBe(false);
    expect(store.roles()).toEqual(['ADMIN']);
  });
});
