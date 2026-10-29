import { Component, OnInit } from '@angular/core';
import { PanelMenuModule } from 'primeng/panelmenu';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-aside',
  standalone: true,
  imports: [PanelMenuModule],
  templateUrl: './aside.component.html',
  styleUrl: './aside.component.css'
})
export class AsideComponent implements OnInit {
  items: MenuItem[] = [];

  ngOnInit(): void {
    this.items = [
      {
        label: 'Inicio',
        icon: 'pi pi-home',
        routerLink: ['/inicio']
      },
      {
        label: 'Gestión Veterinaria',
        icon: 'pi pi-folder',
        expanded: true,
        items: [
          { label: 'Pacientes / Mascotas', icon: 'pi pi-heart', routerLink: ['/mascotas'] },
          { label: 'Owners', icon: 'pi pi-users', routerLink: ['/owners'] },
          { label: 'Consultas Médicas', icon: 'pi pi-paperclip', routerLink: ['/consultas'] }
        ]
      }
    ];
  }
}
