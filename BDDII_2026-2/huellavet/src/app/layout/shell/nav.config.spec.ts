import { visibleNav } from './nav.config';

describe('visibleNav', () => {
  it('only shows the dashboard when all of its API permissions are granted', () => {
    const granted = new Set([
      'GET /api/v1/sales',
      'GET /api/v1/products',
      'GET /api/v1/owners',
    ]);

    const complete = visibleNav((permission) => granted.has(permission));
    const dashboard = complete.flatMap((group) => group.items)
      .find((item) => item.routerLink === '/dashboard');
    expect(dashboard).toBeDefined();

    granted.delete('GET /api/v1/owners');
    const incomplete = visibleNav((permission) => granted.has(permission));
    expect(
      incomplete.flatMap((group) => group.items)
        .some((item) => item.routerLink === '/dashboard')
    ).toBe(false);
  });

  it('shows payment and audit pages only with their read permissions', () => {
    const granted = new Set([
      'GET /api/v1/payments',
      'GET /api/v1/payment-audits',
    ]);

    const items = visibleNav((permission) => granted.has(permission))
      .flatMap((group) => group.items);
    expect(items.some((item) => item.routerLink === '/pagos-citas')).toBe(true);
    expect(items.some((item) => item.routerLink === '/auditoria-pagos')).toBe(true);

    granted.delete('GET /api/v1/payment-audits');
    const restrictedItems = visibleNav((permission) => granted.has(permission))
      .flatMap((group) => group.items);
    expect(restrictedItems.some((item) => item.routerLink === '/auditoria-pagos')).toBe(false);
  });
});
