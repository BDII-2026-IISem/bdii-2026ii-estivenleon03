import { Component, effect, inject, input, output } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { TextareaModule } from 'primeng/textarea';
import { ProductType, ProductTypePayload } from '../../../core/models/product-type.model';

@Component({
  selector: 'app-product-type-form',
  standalone: true,
  imports: [ButtonModule, InputTextModule, MessageModule, ReactiveFormsModule, TextareaModule],
  templateUrl: './product-type-form.html',
  styleUrl: './product-type-form.css',
  host: { class: 'block' },
})
export class ProductTypeForm {
  readonly productType = input<ProductType | null>(null);
  readonly resetKey = input(0);
  readonly saving = input(false);

  readonly saved = output<ProductTypePayload>();
  readonly cancelled = output<void>();

  private readonly fb = inject(NonNullableFormBuilder);

  readonly form = this.fb.group({
    name: [
      '',
      [Validators.required, Validators.pattern(/\S/), Validators.minLength(2), Validators.maxLength(100)],
    ],
    description: ['', [Validators.maxLength(255)]],
  });

  constructor() {
    effect(() => {
      const current = this.productType();
      this.resetKey();
      this.form.reset({
        name: current?.name ?? '',
        description: current?.description ?? '',
      });
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const val = this.form.getRawValue();
    this.saved.emit({
      name: val.name.trim(),
      description: val.description.trim() || null,
    });
  }
}
