import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth-guard';
import { Shell } from './layout/shell/shell';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login').then((m: any) => m.Login || m.default),
  },
  {
    path: '',
    component: Shell,
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard').then((m: any) => m.Dashboard || m.default),
      },
      {
        path: 'profile',
        loadComponent: () => import('./features/auth/profile/profile').then((m: any) => m.Profile || m.default),
      },
      {
        path: 'owners',
        loadComponent: () => import('./features/propietarios/propietario-list/propietario-list').then((m: any) => m.PropietarioList || m.default),
      },
      {
        path: 'mascotas',
        loadComponent: () => import('./features/mascotas/mascotas.component').then((m) => m.MascotasComponent),
      },
      {
        path: 'citas',
        loadComponent: () => import('./features/appointments/appointment-list/appointment-list').then((m) => m.AppointmentList),
      },
      {
        path: 'consultas',
        loadComponent: () => import('./features/consultas/consultas.component').then((m) => m.ConsultasComponent),
      },
      {
        path: 'tratamientos',
        loadComponent: () => import('./features/clinical-treatments/clinical-treatments').then((m) => m.ClinicalTreatments),
      },
      {
        path: 'tipos-producto',
        loadComponent: () => import('./features/product-types/product-type-list/product-type-list').then((m: any) => m.ProductTypeList || m.default),
      },
      {
        path: 'productos',
        loadComponent: () => import('./features/products/product-list/product-list').then((m: any) => m.ProductList || m.default),
      },
      {
        path: 'ventas',
        loadComponent: () => import('./features/sales/sale-list/sale-list').then((m: any) => m.SaleList || m.default),
      },
      {
        path: 'detalle-ventas',
        loadComponent: () => import('./features/product-sales/product-sale-list/product-sale-list').then((m: any) => m.ProductSaleList || m.default),
      },
      {
        path: 'ventas/:id',
        loadComponent: () => import('./features/sales/sale-detail/sale-detail').then((m: any) => m.SaleDetail || m.default),
      },
      {
        path: 'admin/usuarios',
        loadComponent: () => import('./features/admin/users/user-list/user-list').then((m: any) => m.UserList || m.default),
      },
      {
        path: 'admin/roles',
        loadComponent: () => import('./features/admin/roles/role-list/role-list').then((m: any) => m.RoleList || m.default),
      },
      {
        path: 'admin/recursos',
        loadComponent: () => import('./features/admin/resources/resource-list/resource-list').then((m: any) => m.ResourceList || m.default),
      },
      {
        path: 'admin/asignaciones',
        loadComponent: () => import('./features/admin/role-users/role-user-list/role-user-list').then((m: any) => m.RoleUserList || m.default),
      },
      {
        path: 'admin/permisos',
        loadComponent: () => import('./features/admin/resource-roles/resource-role-list/resource-role-list').then((m: any) => m.ResourceRoleList || m.default),
      },
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full',
      },
    ],
  },
  {
    path: '**',
    redirectTo: 'login',
  },
];
