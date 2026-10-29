import { Component, effect, inject, input, output } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { SelectModule } from 'primeng/select';
import { ProductType } from '../../../core/models/product-type.model';
import { Product, ProductPayload } from '../../../core/models/product.model';

@Component({
  selector: 'app-product-form',
  standalone: true,
  imports: [
    ButtonModule,
    InputNumberModule,
    InputTextModule,
    MessageModule,
    ReactiveFormsModule,
    SelectModule,
  ],
  templateUrl: './product-form.html',
  styleUrl: './product-form.css',
  host: { class: 'block' },
})
export class ProductForm {
  readonly product = input<Product | null>(null);
  readonly types = input<ProductType[]>([]);
  readonly resetKey = input(0);
  readonly saving = input(false);

  readonly saved = output<ProductPayload>();
  readonly cancelled = output<void>();

  private readonly fb = inject(NonNullableFormBuilder);

  readonly form = this.fb.group({
    productTypeId: [null as number | null, [Validators.required]],
    name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(120)]],
    brand: ['', [Validators.required, Validators.maxLength(80)]],
    price: [0.01 as number | null, [Validators.required, Validators.min(0.01)]],
    minStock: [0, [Validators.required, Validators.min(0)]],
    quantity: [0, [Validators.required, Validators.min(0)]],
  });

  constructor() {
    effect(() => {
      const current = this.product();
      this.resetKey();
      this.form.reset({
        productTypeId: current?.productTypeId ?? null,
        name: current?.name ?? '',
        brand: current?.brand ?? '',
        price: current ? Number(current.price) : 0.01,
        minStock: current?.minStock ?? 0,
        quantity: current?.quantity ?? 0,
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
      productTypeId: val.productTypeId!,
      name: val.name.trim(),
      brand: val.brand.trim(),
      price: Number(val.price).toFixed(2),
      minStock: val.minStock,
      quantity: val.quantity,
    });
  }
}
