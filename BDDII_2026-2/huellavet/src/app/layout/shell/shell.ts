import { Component, computed, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MenuItem } from 'primeng/api';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { DrawerModule } from 'primeng/drawer';
import { ToastModule } from 'primeng/toast';
import { watchMediaQuery } from '../../core/utils/media-query';
import { SessionStore } from '../../core/services/session-store';
import { AuthService } from '../../core/services/auth';
import { NotificationService } from '../../core/services/notification.service';
import { Aside } from '../aside/aside';
import { Footer } from '../footer/footer';
import { Header } from '../header/header';
import { visibleNav } from './nav.config';

@Component({
  host: { class: 'block' },
  selector: 'app-shell',
  standalone: true,
  imports: [
    RouterOutlet,
    Aside,
    ConfirmDialogModule,
    DrawerModule,
    Footer,
    Header,
    ToastModule,
  ],
  templateUrl: './shell.html',
})
export class Shell {
  private readonly isDesktop = watchMediaQuery('(min-width: 1024px)');
  private readonly session = inject(SessionStore);
  private readonly auth = inject(AuthService);
  private readonly notify = inject(NotificationService);

  readonly sidebarCollapsed = signal(false);
  readonly mobileOpen = signal(false);

  readonly items = computed<MenuItem[]>(() =>
    visibleNav((p) => this.session.canPermission(p)).flatMap((group) =>
      group.items.map((item) => ({
        label: item.label,
        icon: item.icon,
        routerLink: item.routerLink,
      }))
    )
  );

  protected onMenuToggle(): void {
    if (this.isDesktop()) {
      this.sidebarCollapsed.update((collapsed) => !collapsed);
      return;
    }
    this.mobileOpen.set(true);
  }

  refreshPermissions(): void {
    this.auth.me().subscribe({
      next: () => this.notify.success('Permisos actualizados', 'Matriz de sesión sincronizada.'),
    });
  }
}
