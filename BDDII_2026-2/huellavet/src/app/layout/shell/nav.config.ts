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
      { label: 'Panel', icon: 'pi pi-chart-bar', routerLink: '/dashboard', permission: 'GET /api/v1/payments' },
      { label: 'Owners', icon: 'pi pi-users', routerLink: '/owners', permission: 'GET /api/v1/owners' },
      { label: 'Mascotas', icon: 'pi pi-heart', routerLink: '/mascotas', permission: 'GET /api/v1/pets' },
      { label: 'Citas', icon: 'pi pi-calendar', routerLink: '/citas', permission: 'GET /api/v1/appointments' },
      { label: 'Consultas', icon: 'pi pi-file-edit', routerLink: '/consultas', permission: 'GET /api/v1/consultations' },
      { label: 'Prescripciones y vacunas', icon: 'pi pi-heart-fill', routerLink: '/tratamientos', permission: 'GET /api/v1/prescriptions' },
      { label: 'Tipos de Producto', icon: 'pi pi-tags', routerLink: '/tipos-producto', permission: 'GET /api/v1/product-types' },
      { label: 'Productos / Insumos', icon: 'pi pi-box', routerLink: '/productos', permission: 'GET /api/v1/products' },
      { label: 'Ventas y Servicios', icon: 'pi pi-shopping-cart', routerLink: '/ventas', permission: 'GET /api/v1/sales' },
      { label: 'Líneas de Venta', icon: 'pi pi-list', routerLink: '/detalle-ventas', permission: 'GET /api/v1/sales' },
    ],
  },
  {
    label: 'Seguridad',
    items: [
      { label: 'Usuarios', icon: 'pi pi-user', routerLink: '/admin/usuarios', permission: 'GET /api/v1/users' },
      { label: 'Roles', icon: 'pi pi-id-card', routerLink: '/admin/roles', permission: 'GET /api/v1/roles' },
      { label: 'Recursos', icon: 'pi pi-server', routerLink: '/admin/recursos', permission: 'GET /api/v1/permissions' },
      { label: 'Asignaciones', icon: 'pi pi-link', routerLink: '/admin/asignaciones', permission: 'GET /api/v1/user-roles' },
      { label: 'Concesiones', icon: 'pi pi-key', routerLink: '/admin/permisos', permission: 'GET /api/v1/role-permissions' },
    ],
  },
];
