import { Directive, TemplateRef, ViewContainerRef, effect, inject, input } from '@angular/core';
import { SessionStore } from '../../core/services/session-store';

@Directive({
  selector: '[appHasPermission]',
  standalone: true,
})
export class HasPermission {
  private readonly templateRef = inject(TemplateRef<unknown>);
  private readonly viewContainer = inject(ViewContainerRef);
  private readonly session = inject(SessionStore);

  readonly permission = input.required<string>({ alias: 'appHasPermission' });
  private rendered = false;

  constructor() {
    effect(() => {
      const allowed = this.session.canPermission(this.permission());
      if (allowed && !this.rendered) {
        this.viewContainer.createEmbeddedView(this.templateRef);
        this.rendered = true;
      } else if (!allowed && this.rendered) {
        this.viewContainer.clear();
        this.rendered = false;
      }
    });
  }
}
