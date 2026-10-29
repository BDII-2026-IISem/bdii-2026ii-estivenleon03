import { Component, signal } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { DrawerModule } from 'primeng/drawer';
import { watchMediaQuery } from '../../core/utils/media-query';
import { Aside } from '../../layout/aside/aside';
import { Footer } from '../../layout/footer/footer';
import { Header } from '../../layout/header/header';

@Component({
  host: { class: 'block' },
  selector: 'app-construir',
  standalone: true,
  imports: [Aside, ButtonModule, CardModule, DrawerModule, Footer, Header],
  templateUrl: './construir.html',
  styleUrl: './construir.css',
})
export class Construir {
  private readonly isDesktop = watchMediaQuery('(min-width: 1024px)');
  readonly sidebarCollapsed = signal(false);
  readonly mobileOpen = signal(false);
  readonly title = signal('Inicio');

  readonly items: MenuItem[] = [
    { label: 'Inicio', icon: 'pi pi-home', command: () => this.seleccionar('Inicio') },
    { label: 'Clientes / Owners', icon: 'pi pi-users', command: () => this.seleccionar('Clientes / Owners') },
    { label: 'Pacientes / Mascotas', icon: 'pi pi-heart', command: () => this.seleccionar('Pacientes / Mascotas') },
    { label: 'Consultas Médicas', icon: 'pi pi-paperclip', command: () => this.seleccionar('Consultas Médicas') },
    { label: 'Pagos / Ventas', icon: 'pi pi-shopping-cart', command: () => this.seleccionar('Pagos / Ventas') },
  ];

  protected onMenuToggle(): void {
    if (this.isDesktop()) {
      this.sidebarCollapsed.update((collapsed) => !collapsed);
      return;
    }
    this.mobileOpen.set(true);
  }

  protected seleccionar(titulo: string): void {
    this.title.set(titulo);
    this.mobileOpen.set(false);
  }
}
