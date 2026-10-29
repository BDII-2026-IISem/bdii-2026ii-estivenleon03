import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, CanActivateFn, RouterStateSnapshot, UrlTree, provideRouter } from '@angular/router';
import { SessionStore } from '../services/session-store';
import { authGuard } from './auth-guard';
import { permissionGuard } from './permission-guard';

function runGuard(guard: CanActivateFn, url: string, allowed: boolean, data: Record<string, unknown> = {}) {
  TestBed.configureTestingModule({
    providers: [
      provideRouter([]),
      {
        provide: SessionStore,
        useValue: {
          isAuthenticated: () => allowed,
          canPermission: () => allowed,
        },
      },
    ],
  });
  return TestBed.runInInjectionContext(() =>
    guard({ data } as unknown as ActivatedRouteSnapshot, { url } as RouterStateSnapshot)
  );
}

describe('Guards RBAC', () => {
  it('authGuard redirige a /login con returnUrl si no hay sesión', () => {
    const res = runGuard(authGuard, '/owners', false);
    expect(res).toBeInstanceOf(UrlTree);
    expect((res as UrlTree).queryParams['returnUrl']).toBe('/owners');
  });

  it('permissionGuard permite la navegación si el permiso está concedido', () => {
    expect(runGuard(permissionGuard, '/owners', true, { permission: 'GET /api/owners' })).toBe(true);
  });

  it('permissionGuard redirige a /forbidden con el parámetro de permiso faltante', () => {
    const res = runGuard(permissionGuard, '/owners', false, { permission: 'GET /api/owners' });
    expect(res).toBeInstanceOf(UrlTree);
    expect((res as UrlTree).queryParams['permission']).toBe('GET /api/owners');
  });
});
