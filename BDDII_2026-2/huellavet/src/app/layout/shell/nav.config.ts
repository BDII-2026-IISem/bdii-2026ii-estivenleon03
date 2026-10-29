export interface NavItemConfig {
  label: string;
  icon: string;
  routerLink: string;
  permission?: string;
}

export interface NavGroupConfig {
  label: string;
  items: NavItemConfig[];
}

export function visibleNav(can: (permission: string) => boolean): NavGroupConfig[] {
  return NAV.map((group) => ({
    ...group,
    items: group.items.filter((item) => !item.permission || can(item.permission)),
  })).filter((group) => group.items.length > 0);
}

export const NAV: NavGroupConfig[] = [
  {
    label: 'Operación',
    items: [
      { label: 'Panel', icon: 'pi pi-chart-bar', routerLink: '/dashboard', permission: 'GET /api/payments' },
      { label: 'Owners', icon: 'pi pi-users', routerLink: '/owners', permission: 'GET /api/owners' },
      { label: 'Tipos de Producto', icon: 'pi pi-tags', routerLink: '/tipos-producto', permission: 'GET /api/product-types' },
      { label: 'Productos / Insumos', icon: 'pi pi-box', routerLink: '/productos', permission: 'GET /api/vaccines' },
      { label: 'Ventas y Servicios', icon: 'pi pi-shopping-cart', routerLink: '/ventas', permission: 'GET /api/payments' },
      { label: 'Líneas de Venta', icon: 'pi pi-list', routerLink: '/detalle-ventas', permission: 'GET /api/payments' },
    ],
  },
  {
    label: 'Seguridad',
    items: [
      { label: 'Usuarios', icon: 'pi pi-user', routerLink: '/admin/usuarios', permission: 'GET /api/users' },
      { label: 'Roles', icon: 'pi pi-id-card', routerLink: '/admin/roles', permission: 'GET /api/roles' },
      { label: 'Recursos', icon: 'pi pi-server', routerLink: '/admin/recursos', permission: 'GET /api/resources' },
      { label: 'Asignaciones', icon: 'pi pi-link', routerLink: '/admin/asignaciones', permission: 'GET /api/role-users' },
      { label: 'Concesiones', icon: 'pi pi-key', routerLink: '/admin/permisos', permission: 'GET /api/resource-roles' },
    ],
  },
];
