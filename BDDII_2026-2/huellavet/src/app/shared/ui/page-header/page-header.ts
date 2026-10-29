import { Component, input } from '@angular/core';

@Component({
  selector: 'app-page-header',
  standalone: true,
  template: `
    <header class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between border-b border-slate-700 pb-4">
      <div class="flex flex-col gap-1">
        <h1 class="text-2xl font-semibold text-white">{{ title() }}</h1>
        @if (subtitle()) { <p class="text-sm text-slate-400">{{ subtitle() }}</p> }
      </div>
      <div class="flex flex-wrap gap-2"><ng-content /></div>
    </header>
  `,
  host: { class: 'block' },
})
export class PageHeader {
  readonly title = input.required<string>();
  readonly subtitle = input('');
}
