import { Component } from '@angular/core';
import { CardModule } from 'primeng/card';
import { TagModule } from 'primeng/tag';

@Component({
  selector: 'app-placeholder',
  standalone: true,
  imports: [CardModule, TagModule],
  template: `
    <p-tag value="Fase I" severity="warn" [rounded]="true" />
    <p-card header="Pantalla en construcción" class="mt-4">
      <p class="m-0 text-slate-300">El layout ya está montado; esta pantalla se conecta en su respectiva unidad.</p>
    </p-card>
  `,
})
export class Placeholder {}
