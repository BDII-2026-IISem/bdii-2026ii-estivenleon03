import { Component, input } from '@angular/core';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  template: `
    <div class="flex flex-col items-center gap-2 py-10 text-center text-slate-400">
      <i [class]="icon() + ' text-4xl text-slate-500'"></i>
      <p class="font-medium text-slate-300">{{ title() }}</p>
      <p class="text-sm text-slate-500">{{ message() }}</p>
    </div>
  `,
})
export class EmptyState {
  readonly icon = input('pi pi-inbox');
  readonly title = input.required<string>();
  readonly message = input('');
}
